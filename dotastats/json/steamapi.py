from django.conf import settings
import simplejson as json
import urllib
import urllib2
from django.core.cache import get_cache
from dotastats.models.models import SteamAccount


"""
Error codes:
400 = Malformed request (Should log these)
401 = Unauthorized (API Key Bad!)
503 = Overloaded (Our systems, or their systems. Log this.)
"""

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
# NOTE: Validate kargs first.
# TODO: Make me cache viable.
def GetMatchHistory(**kargs):
    json_data = dict()
    try:
        kargs.update({'key': API_KEY})
        url_data = urllib.urlencode(kargs)
        response = urllib2.urlopen(MATCH_HISTORY_URL + '?' + url_data)
        json_data = json.loads(response.read())['result']
        response.close()
    except urllib2.HTTPError, e:
        if e.code() == 400:
            json_data.update({'error': 'Malformed request.'})
        elif e.code() == 401:
            json_data.update({'error': 'Unauthorized API access.'})
        elif e.code() == 503:
            json_data.update({'error': 'Steam servers overloaded.'})
        else:
            json_data.update({'error': 'Unknown HTTP error' + e.code()})


    return json_data

""" NO RESULTS.
{
result: {
status: 1,
num_results: 0,
total_results: 500,
results_remaining: 0,
matches: [ ]
}
}
"""

# TODO: CACHEME
def GetMatchDetails(match_id):
    json_data = dict()
    try:
        kargs = dict({'key': API_KEY, 'match_id': match_id})
        url_data = urllib.urlencode(kargs)
        response = urllib2.urlopen(MATCH_DETAILS_URL + '?' + url_data)
        json_data = json.loads(response.read())['result']
        response.close()
    except urllib2.HTTPError, e:
        if e.code() == 400:
            json_data.update({'error': 'Malformed request.'})
        elif e.code() == 401:
            json_data.update({'error': 'Unauthorized API access.'})
        elif e.code() == 503:
            json_data.update({'error': 'Steam servers overloaded.'})
        else:
            json_data.update({'error': 'Unknown HTTP error' + e.code()})
    
    return json_data
    
# 4294967295 = Private Match
# Dict of player accountids, only retreives names that aren't in the cache.
def GetPlayerNames(player_ids):
    return_dict = dict({4294967295: 'PRIVATE',})
    try:
        cache = get_cache('steam_accounts')
        request_list = []
        
        if type(player_ids) is not list:
            players_ids = [player_ids]
            
        for player_id in player_ids:
            if player_id == 4294967295 or player_id <= 0: # Invalid playerid, assume private
                continue
            player = cache.get(player_id)
            if player == None: # Not in cache. Refresh cache.
                request_list.append(player_id)
            else:
                return_dict.update({player_id: player})
        if len(request_list) != 0:
            response = urllib2.urlopen(STEAM_USER_NAMES + '?' + API_KEY + ','.join(request_list))
            json_data = json.loads(response.read())['response']
            for player in json_data['players']:
                player_obj = SteamAccount(player)
                cache.set(player_id, player_obj)
                return_dict.update({player_id: player_obj})
            response.close()
    except urllib2.HTTPError, e:
        if e.code() == 400:
            return_dict.update({'error': 'Malformed request.'})
        elif e.code() == 401:
            return_dict.update({'error': 'Unauthorized API access.'})
        elif e.code() == 503:
            return_dict.update({'error': 'Steam servers overloaded.'})
        else:
            return_dict.update({'error': 'Unknown HTTP error' + e.code()})
    return return_dict
