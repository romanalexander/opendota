from django.db import models
from datetime import datetime

class SteamPlayer(models.Model):
    steamid = models.BigIntegerField(primary_key=True, unique=True)
    last_refresh = models.DateTimeField(auto_now=True, auto_now_add=True, db_index=True) # Last time this player was checked.
    personaname = models.TextField(db_index=True)
    profileurl = models.TextField(blank=True)
    avatar = models.TextField(blank=True)
    avatarmedium = models.TextField(blank=True)
    avatarfull = models.TextField(blank=True)
    lastlogoff = models.DateTimeField(blank=True) # UNIX time of player last seen.
    
    def get_steam_name(self):
        return self.personaname
    
    @staticmethod
    def from_json_response(json):
        return SteamPlayer(steamid = json.get('steamid'),
                           personaname = json.get('personaname'),
                           profileurl = json.get('profileurl'),
                           avatar = json.get('avatar'),
                           avatarmedium = json.get('avatarmedium'),
                           avatarfull = json.get('avatarfull'),
                           lastlogoff = datetime.fromtimestamp(json.get('lastlogoff')))
      
# To refresh, use django-admin.py getitems
class Items(models.Model):
    item_id = models.IntegerField(primary_key=True) # From the client files.
    client_name = models.TextField()
    
    def __unicode__(self):
        return self.client_name
    
    def get_code_name(self):
        return self.client_name[5:] # Ex: item_blink
    
# To refresh, use django-admin.py getheroes
class Heroes(models.Model):
    hero_id = models.IntegerField(primary_key=True) # From the client files.
    client_name = models.TextField()
    dota2_name = models.TextField()
    
    def __unicode__(self):
        return self.dota2_name
    
    def get_code_name(self):
        return self.client_name[14:] # Ex:  npc_dota_hero_chaos_knight

# Long-running queue of matches to look up.
class MatchHistoryQueue(models.Model):
    match_id = models.BigIntegerField(primary_key=True, unique=True)
    last_refresh = models.DateTimeField(auto_now=True, auto_now_add=True) # Queue will empty FIFO
    start_time = models.DateTimeField() # UNIX Timestamp
    lobby_type = models.DateTimeField()
class MatchHistoryQueuePlayers(models.Model):
    match_history_queue = models.ForeignKey('MatchHistoryQueue')
    account_id = models.BigIntegerField()
    player_slot = models.IntegerField()
    hero_id = models.ForeignKey('Heroes', related_name='+')

def get_game_type(lobby_type): # TODO: Finish & Localize me.
        if lobby_type == 0:
            return 'All Pick'
        elif lobby_type == 1:
            return 'Single Draft'
        elif lobby_type == 2:
            return 'All Random'
        elif lobby_type == 3:
            return 'Random Draft'
        else:
            return str(lobby_type) 

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

class MatchDetails(models.Model):
    match_id = models.BigIntegerField(primary_key=True, unique=True)
    last_refresh = models.DateTimeField(auto_now=True, auto_now_add=True) # Last time this data was accessed for freshness.
    season = models.IntegerField()
    radiant_win = models.BooleanField()
    duration = models.IntegerField() # Seconds of match
    starttime = models.DateTimeField() # UNIX Timestamp
    tower_status_radiant = models.IntegerField()
    tower_status_dire = models.IntegerField()
    barracks_status_radiant = models.IntegerField()
    barracks_status_dire = models.IntegerField()
    cluster = models.IntegerField()
    first_blood_time = models.IntegerField()
    lobby_type = models.IntegerField()
    human_players = models.IntegerField()
    leagueid = models.IntegerField()
    positive_votes = models.IntegerField()
    negative_votes = models.IntegerField()
    game_mode = models.IntegerField()
    
    def get_game_type(self):
        return get_game_type(self.lobby_type)
    
    def __unicode__(self):
        return 'MatchID: ' + self.match_id
    
    @staticmethod
    def from_json_response(json):
        return MatchDetails(
            match_id = json['match_id'],
            season = json['season'],
            radiant_win = json['radiant_win'],
            duration = json['duration'],
            starttime = datetime.fromtimestamp(json['starttime']),
            tower_status_radiant = json['tower_status_radiant'],
            tower_status_dire = json['tower_status_dire'],
            barracks_status_radiant = json['barracks_status_radiant'],
            barracks_status_dire = json['barracks_status_dire'],
            cluster = json['cluster'],
            first_blood_time = json['first_blood_time'],
            lobby_type = json['lobby_type'],
            human_players = json['human_players'],
            leagueid = json['leagueid'],
            positive_votes = json['positive_votes'],
            negative_votes = json['negative_votes'],
            game_mode = json['game_mode'])
    
    class Meta:
        ordering = ('match_id',)
    
class MatchDetailsPlayerEntry(models.Model):
    match_details = models.ForeignKey('MatchDetails')
    account_id = models.ForeignKey(SteamPlayer, related_name='+', db_column='account_id', null=True)
    player_slot = models.IntegerField()
    hero_id = models.ForeignKey('Heroes', related_name='+', db_column='hero_id')
    item_0 = models.ForeignKey('Items', related_name='+', db_column='item_0', null=True)
    item_1 = models.ForeignKey('Items', related_name='+', db_column='item_1', null=True)
    item_2 = models.ForeignKey('Items', related_name='+', db_column='item_2', null=True)
    item_3 = models.ForeignKey('Items', related_name='+', db_column='item_3', null=True)
    item_4 = models.ForeignKey('Items', related_name='+', db_column='item_4', null=True)
    item_5 = models.ForeignKey('Items', related_name='+', db_column='item_5', null=True)
    kills = models.IntegerField()
    deaths = models.IntegerField()
    assists = models.IntegerField()
    leaver_status = models.IntegerField(null=True)
    gold = models.IntegerField()
    last_hits = models.IntegerField()
    denies = models.IntegerField()
    gold_per_min = models.IntegerField()
    xp_per_min = models.IntegerField()
    gold_spent = models.IntegerField()
    hero_damage = models.IntegerField()
    tower_damage = models.IntegerField()
    hero_healing = models.IntegerField()
    level = models.IntegerField()
    
    def get_steam_name(self):
        return steamapi.GetPlayerName(self.account_id_id)
        
    @staticmethod
    def from_json_response(match_details, json):
        return MatchDetailsPlayerEntry(
                match_details = match_details,
                account_id_id=steamapi.convertAccountNumbertoSteam64(json['account_id']), # Store all data in steam64. No reason to have Steam32.
                player_slot=json['player_slot'],
                hero_id_id=json['hero_id'],
                item_0_id=json['item_0'],
                item_1_id=json['item_1'],
                item_2_id=json['item_2'],
                item_3_id=json['item_3'],
                item_4_id=json['item_4'],
                item_5_id=json['item_5'],
                kills=json['kills'],
                deaths=json['deaths'],
                assists=json['assists'],
                leaver_status=json['leaver_status'],
                gold=json['gold'],
                last_hits=json['last_hits'],
                denies=json['denies'],
                gold_per_min=json['gold_per_min'],
                xp_per_min=json['xp_per_min'],
                gold_spent=json['gold_spent'],
                hero_damage=json['hero_damage'],
                tower_damage=json['tower_damage'],
                hero_healing=json['hero_healing'],
                level=json['level'])
        
    class Meta:
        unique_together = (('match_details', 'hero_id', 'player_slot',),) # Every match, only one hero_id per player slot.
        ordering = ('player_slot',)
        
from dotastats.json import steamapi
