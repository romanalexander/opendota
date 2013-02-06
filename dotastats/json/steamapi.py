import simplejson as json
import urllib
import urllib2
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction, connection
from django.core.cache import cache
from dotastats.models import MatchDetails, MatchDetailsPlayerEntry, SteamPlayer, MatchHistoryQueue, MatchHistoryQueuePlayers, MatchPicksBans
from dotastats.exceptions import SteamAPIError

# API Key macro from settings file.
API_KEY = settings.STEAM_API_KEY
MATCH_HISTORY_URL = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchHistory/V001/'
MATCH_DETAILS_URL = 'https://api.steampowered.com/IDOTA2Match_570/GetMatchDetails/V001/'
STEAM_USER_NAMES = 'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/'

""" kargs
player_name=<name> # Search matches with a player name, exact match only
hero_id=<id> # Search for matches with a specific hero being played, hero id's are in dota/scripts/npc/npc_heroes.txt in your Dota install directory
skill=<skill>  # 0 for any, 1 for normal, 2 for high, 3 for very high skill
date_min=<date> # date in UTC seconds since Jan 1, 1970 (unix time format)
date_max=<date> # date in UTC seconds since Jan 1, 1970 (unix time format)
account_id=<id> # Steam account id (this is not SteamID, its only the account number portion)
league_id=<id> # matches for a particular league
start_at_match_id=<id> # Start the search at the indicated match id, descending
matches_requested=<n> # Defaults is 25 matches, this can limit to less
"""
"""
        "dota_game_mode_0"                                                "ALL PICK"
        "dota_game_mode_1"                                                "SINGLE DRAFT"
        "dota_game_mode_2"                                                "ALL RANDOM"
        "dota_game_mode_3"                                                "RANDOM DRAFT"
        "dota_game_mode_4"                                                "CAPTAINS DRAFT"
        "dota_game_mode_5"                                                "CAPTAINS MODE"
        "dota_game_mode_6"                                                "DEATH MODE"
        "dota_game_mode_7"                                                "DIRETIDE"
        "dota_game_mode_8"                                                "REVERSE CAPTAINS MODE"
        "dota_game_mode_9"                                                "The Greeviling"
        "dota_game_mode_10"                                                "TUTORIAL"
        "dota_game_mode_11"                                                "MID ONLY"
        "dota_game_mode_12"                                                "LEAST PLAYED"
        "dota_game_mode_13"                                                "NEW PLAYER POOL"
"""
"""
        [leaver_status] => NULL - Player is a bot.
        
        [leaver_status] => 3 - Player has abandoned the game.
        
        [leaver_status] => 1 - Player has left after the game has become safe to leave.
        
        [leaver_status] => 0 - Player has stayed for the entire match.
"""

def GetLatestMatches():
    """ Returns the last 500 matches (sorted by match_seq_num) that were parsed into MatchDetails. """
    return MatchDetails.exclude_low_priority().all().order_by('-match_seq_num')[:500]

@transaction.commit_manually
def GetMatchHistory(**kargs):
    return_history = cache.get('match_history_refresh', None)
    create_queue = [] 
    account_list = []
    try:
        if return_history == None:
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
                    match_history.save() # Save here so the temporary match is created.
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
            cache.set('match_history_refresh', return_history, 300) # Timeout to refresh match history.
        transaction.commit()
    except:
        transaction.rollback()
        raise
    return return_history

@transaction.commit_manually
def GetMatchDetails(matchid):
    bulk_create = []
    account_list = []
    match_details = None
    try:
        try:
            match_details = MatchDetails.objects.get(match_id=matchid)
        except ObjectDoesNotExist:
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

def GetMatchHistoryJson(**kargs):
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

# Converts the 'account number' to Steam64. Does not convert PRIVATE players.
def convertAccountNumbertoSteam64(steamID):
    if steamID == 4294967295 or steamID == None:
        return None
    else:
        return steamID + 76561197960265728
    
# Does the opposite of convertAccountNumbertoSteam64 and converts the Steam64 down to AccountNumber. 
def convertSteam64toAccountNumber(steamID):
    if steamID == 4294967295 or steamID == None:
        return None
    else:
        return steamID - 76561197960265728

# Only retreives name from cache. Doesn't load into cache or perform WebAPI lookups.
def GetPlayerName(player_id):
    if player_id == 4294967295 or player_id == None:
        return 'Private'
    try: 
        return SteamPlayer.objects.get(pk=player_id).get_steam_name()
    except ObjectDoesNotExist:
        return 'Critical Cache Failure'

# Loads names into cache.
# Returns: Dict of player accountids, only retreives names that aren't in the cache.
def GetPlayerNames(player_ids):
    return_dict = dict({4294967295: 'PRIVATE',})
    try:
        request_list = []
        if type(player_ids) is not list: # Always make sure player_ids is a list.
            player_ids = [player_ids,]
        for player_id in player_ids:
            if player_id == 4294967295 or player_id == None: # Invalid playerid, assume private
                continue
            try:
                player = SteamPlayer.objects.get(pk=player_id)
            except ObjectDoesNotExist:
                request_list.append(player_id)
            else:
                return_dict.update({player_id: player})
        if len(request_list) != 0: # Only allowed 100 users per request. Must split it up.
            do_this = True
            while do_this == True:
                sliced_list = request_list[:100] # Get first 100 elements
                if len(request_list) > 100:
                    request_list = request_list[100:] # Get everything but first 100 elements.
                else:
                    do_this = False # No longer over 100. Don't need to do this again.
                response = urllib2.urlopen(STEAM_USER_NAMES + '?key=' + API_KEY + '&steamids=' + ','.join(str(req) for req in sliced_list)) # TODO: Clean me for clarity.
                json_data = json.loads(response.read())['response']
                bulk_create = []
                for player in json_data['players']:
                    steamplayer = SteamPlayer.from_json_response(player)
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

