# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'MatchDetailsPlayerEntry.additional_units'
        db.add_column('dotastats_matchdetailsplayerentry', 'additional_units',
                      self.gf('django.db.models.fields.TextField')(null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'MatchDetailsPlayerEntry.additional_units'
        db.delete_column('dotastats_matchdetailsplayerentry', 'additional_units')


    models = {
        'dotastats.heroes': {
            'Meta': {'object_name': 'Heroes'},
            'client_name': ('django.db.models.fields.TextField', [], {}),
            'dota2_name': ('django.db.models.fields.TextField', [], {}),
            'hero_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        'dotastats.items': {
            'Meta': {'object_name': 'Items'},
            'client_name': ('django.db.models.fields.TextField', [], {}),
            'item_id': ('django.db.models.fields.IntegerField', [], {'primary_key': 'True'})
        },
        'dotastats.matchdetails': {
            'Meta': {'ordering': "('match_id',)", 'object_name': 'MatchDetails'},
            'barracks_status_dire': ('django.db.models.fields.IntegerField', [], {}),
            'barracks_status_radiant': ('django.db.models.fields.IntegerField', [], {}),
            'cluster': ('django.db.models.fields.IntegerField', [], {}),
            'duration': ('django.db.models.fields.IntegerField', [], {}),
            'first_blood_time': ('django.db.models.fields.IntegerField', [], {}),
            'game_mode': ('django.db.models.fields.IntegerField', [], {}),
            'human_players': ('django.db.models.fields.IntegerField', [], {}),
            'last_refresh': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'leagueid': ('django.db.models.fields.IntegerField', [], {}),
            'lobby_type': ('django.db.models.fields.IntegerField', [], {}),
            'match_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'match_seq_num': ('django.db.models.fields.BigIntegerField', [], {}),
            'negative_votes': ('django.db.models.fields.IntegerField', [], {}),
            'positive_votes': ('django.db.models.fields.IntegerField', [], {}),
            'radiant_win': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'season': ('django.db.models.fields.IntegerField', [], {}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {}),
            'tower_status_dire': ('django.db.models.fields.IntegerField', [], {}),
            'tower_status_radiant': ('django.db.models.fields.IntegerField', [], {})
        },
        'dotastats.matchdetailsplayerentry': {
            'Meta': {'ordering': "('player_slot',)", 'unique_together': "(('match_details', 'hero_id', 'player_slot'),)", 'object_name': 'MatchDetailsPlayerEntry'},
            'ability_upgrades': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'account_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'db_column': "'account_id'", 'to': "orm['dotastats.SteamPlayer']"}),
            'additional_units': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'assists': ('django.db.models.fields.IntegerField', [], {}),
            'deaths': ('django.db.models.fields.IntegerField', [], {}),
            'denies': ('django.db.models.fields.IntegerField', [], {}),
            'gold': ('django.db.models.fields.IntegerField', [], {}),
            'gold_per_min': ('django.db.models.fields.IntegerField', [], {}),
            'gold_spent': ('django.db.models.fields.IntegerField', [], {}),
            'hero_damage': ('django.db.models.fields.IntegerField', [], {}),
            'hero_healing': ('django.db.models.fields.IntegerField', [], {}),
            'hero_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'db_column': "'hero_id'", 'to': "orm['dotastats.Heroes']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_bot': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'item_0': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'db_column': "'item_0'", 'to': "orm['dotastats.Items']"}),
            'item_1': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'db_column': "'item_1'", 'to': "orm['dotastats.Items']"}),
            'item_2': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'db_column': "'item_2'", 'to': "orm['dotastats.Items']"}),
            'item_3': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'db_column': "'item_3'", 'to': "orm['dotastats.Items']"}),
            'item_4': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'db_column': "'item_4'", 'to': "orm['dotastats.Items']"}),
            'item_5': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'db_column': "'item_5'", 'to': "orm['dotastats.Items']"}),
            'kills': ('django.db.models.fields.IntegerField', [], {}),
            'last_hits': ('django.db.models.fields.IntegerField', [], {}),
            'leaver_status': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {}),
            'match_details': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dotastats.MatchDetails']"}),
            'player_slot': ('django.db.models.fields.IntegerField', [], {}),
            'tower_damage': ('django.db.models.fields.IntegerField', [], {}),
            'xp_per_min': ('django.db.models.fields.IntegerField', [], {})
        },
        'dotastats.matchhistoryqueue': {
            'Meta': {'object_name': 'MatchHistoryQueue'},
            'last_refresh': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'lobby_type': ('django.db.models.fields.IntegerField', [], {}),
            'match_id': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'primary_key': 'True'}),
            'match_seq_num': ('django.db.models.fields.BigIntegerField', [], {}),
            'start_time': ('django.db.models.fields.DateTimeField', [], {})
        },
        'dotastats.matchhistoryqueueplayers': {
            'Meta': {'ordering': "('player_slot',)", 'unique_together': "(('match_history_queue', 'hero_id', 'player_slot'),)", 'object_name': 'MatchHistoryQueuePlayers'},
            'account_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'null': 'True', 'db_column': "'account_id'", 'to': "orm['dotastats.SteamPlayer']"}),
            'hero_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'db_column': "'hero_id'", 'to': "orm['dotastats.Heroes']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_bot': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'match_history_queue': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dotastats.MatchHistoryQueue']"}),
            'player_slot': ('django.db.models.fields.IntegerField', [], {})
        },
        'dotastats.matchpicksbans': {
            'Meta': {'ordering': "('order',)", 'unique_together': "(('match_details', 'hero_id', 'order'),)", 'object_name': 'MatchPicksBans'},
            'hero_id': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'+'", 'db_column': "'hero_id'", 'to': "orm['dotastats.Heroes']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_pick': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'match_details': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['dotastats.MatchDetails']"}),
            'order': ('django.db.models.fields.IntegerField', [], {}),
            'team': ('django.db.models.fields.IntegerField', [], {})
        },
        'dotastats.steamplayer': {
            'Meta': {'object_name': 'SteamPlayer'},
            'avatar': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'avatarfull': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'avatarmedium': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'last_refresh': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'lastlogoff': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'personaname': ('django.db.models.fields.TextField', [], {}),
            'profileurl': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'steamid': ('django.db.models.fields.BigIntegerField', [], {'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['dotastats']