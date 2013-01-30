import simplejson as json
import urllib
import urllib2
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from dotastats.models import MatchDetails, MatchDetailsPlayerEntry, SteamPlayer
from django.db import transaction

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

# Takes in GetMatchHistoryJson, hits DB cache or asks WebAPI.
# TODO: Cache results. (Don't rely on page cache only.)
def GetMatchHistory(**kargs):
    return GetMatchHistoryJson(**kargs)

@transaction.commit_manually
def GetMatchDetails(matchid):
    bulk_create = []
    account_list = []
    match_details = None
    try:
        try:
            match_details = MatchDetails.objects.get(match_id=matchid)
        except ObjectDoesNotExist:
            json_data = GetMatchDetailsJson(matchid)
            json_player_data = json_data['players']
            match_details = MatchDetails.from_json_response(json_data)
            match_details.save()        
            for json_player in json_player_data:
                bulk_create.append(MatchDetailsPlayerEntry.from_json_response(match_details, json_player))
                account_list.append(convertAccountNumbertoSteam64(json_player['account_id']))
        GetPlayerNames(account_list) # Make sure names are loaded into cache.
        if match_details != None:
            match_details.matchdetailsplayerentry_set.bulk_create(bulk_create)
        transaction.commit()
    except:
        transaction.rollback()
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
            json_data.update({'error': 'Malformed request.'})
        elif e.code == 401:
            json_data.update({'error': 'Unauthorized API access.'})
        elif e.code == 503:
            json_data.update({'error': 'Steam servers overloaded.'})
        else:
            json_data.update({'error': 'Unknown HTTP error' + e.code})
            
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
            json_data.update({'error': 'Malformed request.'})
        elif e.code == 401:
            json_data.update({'error': 'Unauthorized API access.'})
        elif e.code == 503:
            json_data.update({'error': 'Steam servers overloaded.'})
        else:
            json_data.update({'error': 'Unknown HTTP error' + e.code})
    
    return json_data

# Converts the 'account number' to Steam64. Does not convert PRIVATE players.
def convertAccountNumbertoSteam64(steamID):
    if steamID == 4294967295:
        return None
    else:
        return steamID + 76561197960265728
    
# Does the opposite of convertAccountNumbertoSteam64 and converts the Steam64 down to AccountNumber. 
def convertSteam64toAccountNumber(steamID):
    if steamID == 4294967295:
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
            if player_id == 4294967295: # Invalid playerid, assume private
                continue
            try:
                player = SteamPlayer.objects.get(pk=player_id)
            except ObjectDoesNotExist:
                request_list.append(player_id)
            else:
                return_dict.update({player_id: player})
        if len(request_list) != 0:
            response = urllib2.urlopen(STEAM_USER_NAMES + '?key=' + API_KEY + '&steamids=' + ','.join(str(req) for req in request_list)) # TODO: Clean me for clarity.
            json_data = json.loads(response.read())['response']
            bulk_create = []
            for player in json_data['players']:
                steamplayer = SteamPlayer.from_json_response(player)
                bulk_create.append(steamplayer)
            SteamPlayer.objects.bulk_create(bulk_create)
            response.close()
    except urllib2.HTTPError, e:
        if e.code == 400:
            return_dict.update({'error': 'Malformed request.'})
        elif e.code == 401:
            return_dict.update({'error': 'Unauthorized API access.'})
        elif e.code == 503:
            return_dict.update({'error': 'Steam servers overloaded.'})
        else:
            return_dict.update({'error': 'Unknown HTTP error' + e.code})
            
    return return_dict

