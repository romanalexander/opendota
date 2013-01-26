from django.db import models

class SteamAccount(): # Not a DB model, used for caching purposes.
    def __init__(self, values_dict):
        self.values_dict = values_dict
    
    """def __getattr__(self, attr):
        if attr in self.values_dict:
            return self.values[attr]
        raise AttributeError("Object has no attribute %r" % attr)"""
        

class MatchDetails(models.Model):
    match_id = models.BigIntegerField(primary_key=True, unique=True)
    last_refresh = models.DateTimeField(auto_now=True, auto_now_add=True) # Last time this data was accessed for freshness.
    season = models.IntegerField()
    radiant_win = models.BooleanField()
    duration = models.IntegerField() # Seconds of match
    starttime = models.BigIntegerField() # UNIX Timestamp
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
    
class MatchDetailsPlayerEntry(models.Model):
    match_details = models.ForeignKey('MatchDetails')
    account_id = models.BigIntegerField(db_index=True)
    player_slot = models.IntegerField()
    hero_id = models.IntegerField()
    item_0 = models.IntegerField()
    item_1 = models.IntegerField()
    item_2 = models.IntegerField()
    item_3 = models.IntegerField()
    item_4 = models.IntegerField()
    item_5 = models.IntegerField()
    kills = models.IntegerField()
    deaths = models.IntegerField()
    assists = models.IntegerField()
    leaver_status = models.IntegerField()
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
        return steamapi.GetPlayerName(self.account_id)
        
    class Meta:
        ordering = ('player_slot',)
        
        
from dotastats.json import steamapi
