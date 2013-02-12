import simplejson as json
import urllib
import urllib2
from datetime import datetime
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, connection
from django.core.cache import cache
from django.utils import timezone
from dotastats.models import MatchDetails, MatchDetailsPlayerEntry, SteamPlayer, MatchHistoryQueue, MatchHistoryQueuePlayers, MatchPicksBans
from dotastats.exceptions import SteamAPIError

# API Key macro from settings file.
API_KEY = settings.STEAM_API_KEY
MATCH_FRESHNESS = settings.DOTA_MATCH_REFRESH
PLAYER_FRESHNESS = settings.DOTA_PLAYER_REFRESH
MATCH_HISTORY_URL = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/'
MATCH_DETAILS_URL = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/'
STEAM_USER_NAMES = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'

def GetLatestMatches():
    """Returns the last 500 matches (sorted by match_seq_num) that were parsed into MatchDetails. 
    """
    return MatchDetails.exclude_low_priority().all().order_by('-match_seq_num')[:500]

@transaction.commit_manually
def GetMatchHistory(**kargs):
    """Loads items into MatchHistoryQueue.
    This will poll the WebAPI and acquire a list of matches. This will never return a match that has already been processed into MatchDetails.
    
    Args:
        **kargs (dict): kargs to pass into the WebAPI for filtering lookups. Valid kargs are:
            player_name=<name> # Search matches with a player name, exact match only
            hero_id=<id> # Search for matches with a specific hero being played, hero id's are in dota/scripts/npc/npc_heroes.txt in your Dota install directory
            skill=<skill>  # 0 for any, 1 for normal, 2 for high, 3 for very high skill
            date_min=<date> # date in UTC seconds since Jan 1, 1970 (unix time format)
            date_max=<date> # date in UTC seconds since Jan 1, 1970 (unix time format)
            account_id=<id> # Steam account id (this is not SteamID, its only the account number portion)
            league_id=<id> # matches for a particular league
            start_at_match_id=<id> # Start the search at the indicated match id, descending
            matches_requested=<n> # Defaults is 25 matches, this can limit to less
            
    Returns:
        A list of MatchHistoryQueue objects to be iterated on, sorted by match `start_time`
    """
    create_queue = [] 
    account_list = []
    try:
        json_data = GetMatchHistoryJson(**kargs)
        if json_data['status'] == 15: # Match history denied, is set to private.
            raise SteamAPIError("This user has his DotA2 Profile set to private.")
        with connection.constraint_checks_disabled():
            for match in json_data['matches']:
                if(len(match['players']) < 1): # Don't log matches without players.
                    continue
                bulk_json = []
                json_player_data = match['players']
                if MatchDetails.objects.filter(pk=match['match_id']).exists() or MatchHistoryQueue.objects.filter(pk=match['match_id']).exists() or match['lobby_type'] == 4:
                    continue # Object in queue or already created. Can ignore for now.
                match_history = MatchHistoryQueue.from_json_response(match)
                match_history.save() # Save here so the pk is created.
                for json_player in json_player_data:
                    bulk_json.append(json_player)
                    account_list.append(convertAccountNumbertoSteam64(json_player.get('account_id', None)))
                create_queue.append((match_history, bulk_json))
            GetPlayerNames(account_list) # Loads accounts into cache
            for create_match_history, json_player_list in create_queue:
                queue_player_set = []
                for json_player in json_player_list:
                    queue_player_set.append(MatchHistoryQueuePlayers.from_json_response(create_match_history, json_player))
                create_match_history.matchhistoryqueueplayers_set.bulk_create(queue_player_set)
        return_history = MatchHistoryQueue.objects.all().order_by('-start_time')
        transaction.commit()
    except:
        transaction.rollback()
        raise
    return return_history

@transaction.commit_manually
def CreateMatchDetails(matchid):
    """This creates a MatchDetails object by matchid. 
    If a MatchDetails object already exists, it is deleted and recreated.
    WARNING: This method is volatile, and will always delete a conflicting duplicate match. See ``GetMatchDetails`` for a non-volatile lookup method.
    
    Args:
        matchid (int): Valid MatchID to parse.
        
    Returns:
        The newly created MatchDetails object.
    
    """
    bulk_create = []
    account_list = []
    match_details = None
    MatchDetails.objects.filter(match_id=matchid).all().delete() # Delete all previous MatchDetails.
    try:
        try:
            json_data = GetMatchDetailsJson(matchid)
        except urllib2.HTTPError, e:
            if e.code == 401: # Unauthorized to view lobby. Return None
                MatchHistoryQueue.objects.filter(match_id=matchid).all().delete() # Remove from queue.
                transaction.commit() # Make sure the deletion goes through before raising error.
                raise SteamAPIError("This lobby is password protected.")
            else:
                raise
        json_player_data = json_data['players']
        match_details = MatchDetails.from_json_response(json_data)
        match_details.save()
        json_picks_bans_data = json_data.get('picks_bans', False)
        if json_picks_bans_data:
            picks_bans_bulk_create = []
            for json_picks_bans in json_picks_bans_data:
                picks_bans_bulk_create.append(MatchPicksBans.from_json_response(match_details, json_picks_bans))
            MatchPicksBans.objects.bulk_create(picks_bans_bulk_create)
        for json_player in json_player_data:
            bulk_create.append(MatchDetailsPlayerEntry.from_json_response(match_details, json_player))
            account_list.append(convertAccountNumbertoSteam64(json_player['account_id']))
        GetPlayerNames(account_list) # Loads accounts into db for FK constraints. TODO: Re-work me? Disable FK constraints entirely?
        if match_details != None and len(bulk_create) > 0: 
            match_details.matchdetailsplayerentry_set.bulk_create(bulk_create)
        MatchHistoryQueue.objects.filter(match_id=matchid).all().delete()
        transaction.commit()
    except:
        transaction.rollback()
        raise
    return match_details


def GetMatchDetails(matchid, force_refresh=False):
    """Fetches a MatchDetails object from db cache or newly created from json, by matchid.
    NOTE: This method adheres to ``MATCH_FRESHNESS`` setting. Matches after this threshhold will be recreated.
    
    Args:
        matchid (int): MatchID to look up.
        
    Kwargs:
        force_refresh (bool): Whether to force match freshness.  True will cause a lookup regardless of last_refresh.
        
    Returns:
        A MatchDetails object, old or new.
    
    """
    match_details = None
    try:
        match_details = MatchDetails.objects.get(match_id=matchid)
    except ObjectDoesNotExist:
        match_details = None
    if match_details == None or force_refresh or timezone.now() - match_details.last_refresh > MATCH_FRESHNESS: 
        match_details = CreateMatchDetails(matchid)
    return match_details

def GetMatchHistoryJson(**kargs):
    """Fetches MatchHistory JSON as dict from WebAPI.
    
    Args:
        **kargs (dict): kwargs to pass to WebAPI for filtering. This is encoded into the url.
        
    Returns:
        dict. The resulting dict of json.loads.
        
    Raises:
        SteamAPIError: An error occured with a recognizable error code.
        HTTPError: Misc. HTTP Error occured.
    """
    json_data = dict()
    try:
        kargs.update({'key': API_KEY})
        url_data = urllib.urlencode(kargs)
        response = urllib2.urlopen(MATCH_HISTORY_URL + '?' + url_data)
        json_data = json.loads(response.read())['result']
        response.close()
    except urllib2.HTTPError, e:
        if e.code == 400:
            raise SteamAPIError("Malformed API request.")
        elif e.code == 401:
            raise SteamAPIError("Unauthorized API access. Please recheck your API key.")
        elif e.code == 503:
            raise SteamAPIError("The Steam servers are currently overloaded.")
        else:
            raise SteamAPIError("Unknown API error" + str(e.code))
        raise
    return json_data

def GetMatchDetailsJson(match_id):
    """Fetches MatchDetails JSON as dict from WebAPI.
    
    Args:
        match_id (int): Valid match_id to pass to the WebAPI.
        
    Returns:
        dict. The resulting dict of json.loads.
        
    Raises:
        SteamAPIError: An error occured with a recognizable error code.
        HTTPError: Misc. HTTP Error occured.
    """
    json_data = dict()
    try:
        kargs = dict({'key': API_KEY, 'match_id': match_id})
        url_data = urllib.urlencode(kargs)
        response = urllib2.urlopen(MATCH_DETAILS_URL + '?' + url_data)
        json_data = json.loads(response.read())['result']
        response.close()
    except urllib2.HTTPError, e:
        if e.code == 400:
            raise SteamAPIError("Malformed API request.")
        elif e.code == 401:
            raise SteamAPIError("Unauthorized API access. Please recheck your API key.")
        elif e.code == 503:
            raise SteamAPIError("The Steam servers are currently overloaded.")
        else:
            raise SteamAPIError("Unknown API error" + str(e.code))
        raise
    return json_data

def convertAccountNumbertoSteam64(steamID):
    """Converts the `account number` to Steam64. Does not convert PRIVATE players.
    This does the opposite of `convertSteam64toAccountNumber`
    
    Args:
        steamID (int): None or SteamID to convert
         
     Returns:
         int or None. None if steamID is 4294967295 or None. Otherwise returns the Steam64 ID. 
    """
    if steamID == 4294967295 or steamID == None:
        return None
    else:
        return steamID + 76561197960265728
 
def convertSteam64toAccountNumber(steamID):
    """Converts the Steam64 to 'account number'. Does not convert PRIVATE players.
    This does the opposite of `convertAccountNumbertoSteam64`
    
    Args:
        steamID (int): None or SteamID to convert
         
     Returns:
         int or None. None if steamID is 4294967295 or None. Otherwise returns the Steam64 ID.
     """
    if steamID == 4294967295 or steamID == None:
        return None
    else:
        return steamID - 76561197960265728

# Only retreives name from cache. Doesn't load into cache or perform WebAPI lookups.
def GetPlayerName(player_id):
    """Retreives the steam name from a Steam64 playerid.
    
    Args:
        player_id (int): None or SteamID to lookup.
        
    Returns:
        string or 'Private' or 'Critical Cache Failure'. Returns Private if player_id is None, or if steam player object does not exist. 
    """
    if player_id == 4294967295 or player_id == None:
        return 'Private'
    try: 
        return SteamPlayer.objects.get(pk=player_id).get_steam_name()
    except ObjectDoesNotExist:
        return 'Critical Cache Failure'

# Loads names into cache.
# Returns: Dict of player accountids, only retreives names that aren't in the cache.
def GetPlayerNames(player_ids):
    """Loads player_ids into Steam Account cache.
    This will take in a list of account ids and load the Steam Accounts into db cache from the Steam API.
    
    Args:
        player_ids (list): List of SteamID64s to lookup.
        
    Returns:
        dict. Returns dict of player_ids to persona_names.
    """
    return_dict = dict({4294967295: 'PRIVATE',})
    try:
        request_list = [] # IDs to request from SteamAPI.
        save_list = dict() # IDs to `save` instead of `create`. (To not invalidate FK constraints)
        if type(player_ids) is not list: # Always make sure player_ids is a list.
            player_ids = [player_ids,]
        for player_id in player_ids:
            if player_id == 4294967295 or player_id == None: # Invalid playerid, assume private
                continue
            try:
                player = SteamPlayer.objects.get(pk=player_id)
                if timezone.now() - player.last_refresh > PLAYER_FRESHNESS:
                    request_list.append(player.pk)
                    save_list[str(player_id)] = player
            except ObjectDoesNotExist:
                request_list.append(player_id)
        if len(request_list) != 0: # Only allowed 100 users per request. Must split it up.
            do_this = True
            while do_this == True:
                sliced_list = request_list[:100] # Get first 100 elements
                if len(request_list) > 100:
                    request_list = request_list[100:] # Get everything but first 100 elements.
                else:
                    do_this = False # No longer over 100. Don't need to do this again.
                response = urllib2.urlopen(STEAM_USER_NAMES + '?key=' + API_KEY + '&steamids=' + ','.join(str(req) for req in sliced_list))
                json_data = json.loads(response.read())['response']
                bulk_create = []
                for player in json_data['players']:
                    steamplayer = SteamPlayer.from_json_response(player)
                    if player['steamid'] in save_list: # If object should be saved instead, save now. Bulk_create will raise IntegrityErrors.
                        steamplayer.save()
                    else:
                        bulk_create.append(steamplayer)
                SteamPlayer.objects.bulk_create(bulk_create)
                response.close()
    except urllib2.HTTPError, e:
        if e.code == 400:
            raise SteamAPIError("Malformed API request.")
        elif e.code == 401:
            raise SteamAPIError("Unauthorized API access. Please recheck your API key.")
        elif e.code == 503:
            raise SteamAPIError("The Steam servers are currently overloaded.")
        else:
            raise SteamAPIError("Unknown API error" + str(e.code))
        raise
    return return_dict

