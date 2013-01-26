import simplejson as json
import urllib
import urllib2, re
from django.conf import settings
from django.core.cache import get_cache
from django.core.exceptions import ObjectDoesNotExist
from dotastats.models.models import SteamAccount, MatchDetails, MatchDetailsPlayerEntry

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

def GetMatchDetails(matchid):
    try:
        match_details = MatchDetails.objects.get(match_id=matchid)
    except ObjectDoesNotExist:
        json_data = GetMatchDetailsJson(matchid)
        json_player_data = json_data['players']
        match_details = MatchDetails( # Don't use raw JSON-dict data. Bad things could happen. This way is verbose, yet correct.
            match_id = json_data['match_id'],
            season = json_data['season'],
            radiant_win = json_data['radiant_win'],
            duration = json_data['duration'],
            starttime = json_data['starttime'],
            tower_status_radiant = json_data['tower_status_radiant'],
            tower_status_dire = json_data['tower_status_dire'],
            barracks_status_radiant = json_data['barracks_status_radiant'],
            barracks_status_dire = json_data['barracks_status_dire'],
            cluster = json_data['cluster'],
            first_blood_time = json_data['first_blood_time'],
            lobby_type = json_data['lobby_type'],
            human_players = json_data['human_players'],
            leagueid = json_data['leagueid'],
            positive_votes = json_data['positive_votes'],
            negative_votes = json_data['negative_votes'],
            game_mode = json_data['game_mode'])
        match_details.save()
        for json_player in json_player_data:
            match_details.matchdetailsplayerentry_set.create(
                account_id=convertAccountNumbertoSteam64(json_player['account_id']), # Store all data in steam64. No reason to have Steam32.
                player_slot=json_player['player_slot'],
                hero_id=json_player['hero_id'],
                item_0=json_player['item_0'],
                item_1=json_player['item_1'],
                item_2=json_player['item_2'],
                item_3=json_player['item_3'],
                item_4=json_player['item_4'],
                item_5=json_player['item_5'],
                kills=json_player['kills'],
                deaths=json_player['deaths'],
                assists=json_player['assists'],
                leaver_status=json_player['leaver_status'],
                gold=json_player['gold'],
                last_hits=json_player['last_hits'],
                denies=json_player['denies'],
                gold_per_min=json_player['gold_per_min'],
                xp_per_min=json_player['xp_per_min'],
                gold_spent=json_player['gold_spent'],
                hero_damage=json_player['hero_damage'],
                tower_damage=json_player['tower_damage'],
                hero_healing=json_player['hero_healing'],
                level=json_player['level'])
    account_list = []
    for player_entry in match_details.matchdetailsplayerentry_set.all():
        account_list.append(player_entry.account_id)
    GetPlayerNames(account_list) # Make sure names are loaded into cache.
    
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
            json_data.update({'error': 'Unknown HTTP error' + e.code()})
            
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
            json_data.update({'error': 'Unknown HTTP error' + e.code()})
    
    return json_data

# Converts the 'account number' to Steam64. Does not convert PRIVATE players.
def convertAccountNumbertoSteam64(steamID):
    if steamID == 4294967295:
        return 4294967295
    else:
        return steamID + 76561197960265728

# Only retreives name from cache. Doesn't load into cache or perform WebAPI lookups.
def GetPlayerName(player_id):
    cache = get_cache('steam_accounts')
    if player_id == 4294967295:
        return 'Private'
    if cache.get(player_id) == None:
        return 'Critical Cache Failure'
    else:
        return cache.get(player_id).values_dict['personaname']

# Loads names into cache.
# Returns: Dict of player accountids, only retreives names that aren't in the cache.
def GetPlayerNames(player_ids):
    return_dict = dict({4294967295: 'PRIVATE',})
    try:
        cache = get_cache('steam_accounts') # Cache used to store SteamAccounts.
        request_list = []
        cache.set(4294967295, 'PRIVATE')
        if type(player_ids) is not list: # Always make sure player_ids is a list.
            players_ids = [player_ids]
            
        for player_id in player_ids:
            if player_id == 4294967295: # Invalid playerid, assume private
                continue
            player = cache.get(player_id)
            if player == None: # Not in cache. Refresh cache.
                request_list.append(player_id)
            else:
                return_dict.update({player_id: player})
        if len(request_list) != 0:
            response = urllib2.urlopen(STEAM_USER_NAMES + '?key=' + API_KEY + '&steamids=' + ','.join(str(req) for req in request_list)) # TODO: Clean me for clarity.
            json_data = json.loads(response.read())['response']
            for player in json_data['players']:
                player_obj = SteamAccount(player)
                cache.set(player_obj.values_dict['steamid'], player_obj)
                return_dict.update({player_id: player_obj})
            response.close()
    except urllib2.HTTPError, e:
        if e.code == 400:
            return_dict.update({'error': 'Malformed request.'})
        elif e.code == 401:
            return_dict.update({'error': 'Unauthorized API access.'})
        elif e.code == 503:
            return_dict.update({'error': 'Steam servers overloaded.'})
        else:
            return_dict.update({'error': 'Unknown HTTP error' + e.code()})
            
    return return_dict

