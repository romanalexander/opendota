# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SteamPlayer'
        db.create_table('dotastats_steamplayer', (
            ('steamid', self.gf('django.db.models.fields.BigIntegerField')(unique=True, primary_key=True)),
            ('last_refresh', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, db_index=True, blank=True)),
            ('personaname', self.gf('django.db.models.fields.TextField')()),
            ('profileurl', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('avatar', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('avatarmedium', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('avatarfull', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('lastlogoff', self.gf('django.db.models.fields.DateTimeField')(null=True)),
        ))
        db.send_create_signal('dotastats', ['SteamPlayer'])

        # Adding model 'Items'
        db.create_table('dotastats_items', (
            ('item_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('client_name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('dotastats', ['Items'])

        # Adding model 'Heroes'
        db.create_table('dotastats_heroes', (
            ('hero_id', self.gf('django.db.models.fields.IntegerField')(primary_key=True)),
            ('client_name', self.gf('django.db.models.fields.TextField')()),
            ('dota2_name', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('dotastats', ['Heroes'])

        # Adding model 'MatchHistoryQueue'
        db.create_table('dotastats_matchhistoryqueue', (
            ('match_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True, primary_key=True)),
            ('last_refresh', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('match_seq_num', self.gf('django.db.models.fields.BigIntegerField')()),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('lobby_type', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('dotastats', ['MatchHistoryQueue'])

        # Adding model 'MatchHistoryQueuePlayers'
        db.create_table('dotastats_matchhistoryqueueplayers', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match_history_queue', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dotastats.MatchHistoryQueue'])),
            ('account_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, db_column='account_id', to=orm['dotastats.SteamPlayer'])),
            ('player_slot', self.gf('django.db.models.fields.IntegerField')()),
            ('hero_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', db_column='hero_id', to=orm['dotastats.Heroes'])),
            ('is_bot', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('dotastats', ['MatchHistoryQueuePlayers'])

        # Adding unique constraint on 'MatchHistoryQueuePlayers', fields ['match_history_queue', 'hero_id', 'player_slot']
        db.create_unique('dotastats_matchhistoryqueueplayers', ['match_history_queue_id', 'hero_id', 'player_slot'])

        # Adding model 'MatchDetails'
        db.create_table('dotastats_matchdetails', (
            ('match_id', self.gf('django.db.models.fields.BigIntegerField')(unique=True, primary_key=True)),
            ('last_refresh', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('match_seq_num', self.gf('django.db.models.fields.BigIntegerField')()),
            ('season', self.gf('django.db.models.fields.IntegerField')()),
            ('radiant_win', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('duration', self.gf('django.db.models.fields.IntegerField')()),
            ('start_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('tower_status_radiant', self.gf('django.db.models.fields.IntegerField')()),
            ('tower_status_dire', self.gf('django.db.models.fields.IntegerField')()),
            ('barracks_status_radiant', self.gf('django.db.models.fields.IntegerField')()),
            ('barracks_status_dire', self.gf('django.db.models.fields.IntegerField')()),
            ('cluster', self.gf('django.db.models.fields.IntegerField')()),
            ('first_blood_time', self.gf('django.db.models.fields.IntegerField')()),
            ('lobby_type', self.gf('django.db.models.fields.IntegerField')()),
            ('human_players', self.gf('django.db.models.fields.IntegerField')()),
            ('leagueid', self.gf('django.db.models.fields.IntegerField')()),
            ('positive_votes', self.gf('django.db.models.fields.IntegerField')()),
            ('negative_votes', self.gf('django.db.models.fields.IntegerField')()),
            ('game_mode', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('dotastats', ['MatchDetails'])

        # Adding model 'MatchPicksBans'
        db.create_table('dotastats_matchpicksbans', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match_details', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dotastats.MatchDetails'])),
            ('is_pick', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('hero_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', db_column='hero_id', to=orm['dotastats.Heroes'])),
            ('team', self.gf('django.db.models.fields.IntegerField')()),
            ('order', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('dotastats', ['MatchPicksBans'])

        # Adding unique constraint on 'MatchPicksBans', fields ['match_details', 'hero_id', 'order']
        db.create_unique('dotastats_matchpicksbans', ['match_details_id', 'hero_id', 'order'])

        # Adding model 'MatchDetailsPlayerEntry'
        db.create_table('dotastats_matchdetailsplayerentry', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('match_details', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dotastats.MatchDetails'])),
            ('account_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, db_column='account_id', to=orm['dotastats.SteamPlayer'])),
            ('player_slot', self.gf('django.db.models.fields.IntegerField')()),
            ('hero_id', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', db_column='hero_id', to=orm['dotastats.Heroes'])),
            ('item_0', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, db_column='item_0', to=orm['dotastats.Items'])),
            ('item_1', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, db_column='item_1', to=orm['dotastats.Items'])),
            ('item_2', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, db_column='item_2', to=orm['dotastats.Items'])),
            ('item_3', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, db_column='item_3', to=orm['dotastats.Items'])),
            ('item_4', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, db_column='item_4', to=orm['dotastats.Items'])),
            ('item_5', self.gf('django.db.models.fields.related.ForeignKey')(related_name='+', null=True, db_column='item_5', to=orm['dotastats.Items'])),
            ('kills', self.gf('django.db.models.fields.IntegerField')()),
            ('deaths', self.gf('django.db.models.fields.IntegerField')()),
            ('assists', self.gf('django.db.models.fields.IntegerField')()),
            ('leaver_status', self.gf('django.db.models.fields.IntegerField')(null=True)),
            ('gold', self.gf('django.db.models.fields.IntegerField')()),
            ('last_hits', self.gf('django.db.models.fields.IntegerField')()),
            ('denies', self.gf('django.db.models.fields.IntegerField')()),
            ('gold_per_min', self.gf('django.db.models.fields.IntegerField')()),
            ('xp_per_min', self.gf('django.db.models.fields.IntegerField')()),
            ('gold_spent', self.gf('django.db.models.fields.IntegerField')()),
            ('hero_damage', self.gf('django.db.models.fields.IntegerField')()),
            ('tower_damage', self.gf('django.db.models.fields.IntegerField')()),
            ('hero_healing', self.gf('django.db.models.fields.IntegerField')()),
            ('level', self.gf('django.db.models.fields.IntegerField')()),
            ('ability_upgrades', self.gf('django.db.models.fields.TextField')(null=True)),
            ('is_bot', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('dotastats', ['MatchDetailsPlayerEntry'])

        # Adding unique constraint on 'MatchDetailsPlayerEntry', fields ['match_details', 'hero_id', 'player_slot']
        db.create_unique('dotastats_matchdetailsplayerentry', ['match_details_id', 'hero_id', 'player_slot'])


    def backwards(self, orm):
        # Removing unique constraint on 'MatchDetailsPlayerEntry', fields ['match_details', 'hero_id', 'player_slot']
        db.delete_unique('dotastats_matchdetailsplayerentry', ['match_details_id', 'hero_id', 'player_slot'])

        # Removing unique constraint on 'MatchPicksBans', fields ['match_details', 'hero_id', 'order']
        db.delete_unique('dotastats_matchpicksbans', ['match_details_id', 'hero_id', 'order'])

        # Removing unique constraint on 'MatchHistoryQueuePlayers', fields ['match_history_queue', 'hero_id', 'player_slot']
        db.delete_unique('dotastats_matchhistoryqueueplayers', ['match_history_queue_id', 'hero_id', 'player_slot'])

        # Deleting model 'SteamPlayer'
        db.delete_table('dotastats_steamplayer')

        # Deleting model 'Items'
        db.delete_table('dotastats_items')

        # Deleting model 'Heroes'
        db.delete_table('dotastats_heroes')

        # Deleting model 'MatchHistoryQueue'
        db.delete_table('dotastats_matchhistoryqueue')

        # Deleting model 'MatchHistoryQueuePlayers'
        db.delete_table('dotastats_matchhistoryqueueplayers')

        # Deleting model 'MatchDetails'
        db.delete_table('dotastats_matchdetails')

        # Deleting model 'MatchPicksBans'
        db.delete_table('dotastats_matchpicksbans')

        # Deleting model 'MatchDetailsPlayerEntry'
        db.delete_table('dotastats_matchdetailsplayerentry')


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