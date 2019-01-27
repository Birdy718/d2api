#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import unittest

import d2api
from d2api.src import endpoints
from d2api.src import entities
from d2api.src import errors as d2errors
from d2api.src import wrappers
from d2api import update_local_data


class APIPreliminaryTests(unittest.TestCase):
    def test_environment_api_key_set(self):
        self.assertIsNotNone(os.environ.get('D2_API_KEY'), 
        'D2_API_KEY was not set in environment')

    def test_correct_api_key(self):
        key = 'abcdxyz'
        tmp_api = d2api.APIWrapper(key)

        with self.assertRaises(d2errors.APIAuthenticationError, 
        msg = f'Request with API key \'{key}\' should raise authentication error'):
            tmp_api.get_match_details('4176987886')
    
    def test_insufficient_params(self):
        with self.assertRaises(d2errors.APIInsufficientArguments, msg = "match_id is a required argument for get_match_details"):
            d2api.APIWrapper().get_match_details(match_id = None)

    def test_logger_check(self):
        tmp_api = d2api.APIWrapper(logging_enabled = True)
        self.assertIsNotNone(tmp_api.logger, 
        'Logger should not be None when \'logging_enabled\' was set to True')

    def test_update_local_files(self):
        self.assertNotEqual(update_local_data(), {},
        msg = "Update must return remote metadata. Instead, it returned an empty dict.")

    def test_unparsed_results_dtype(self):
        api = d2api.APIWrapper(parse_results = False)
        self.assertIsInstance(api.get_match_history(), dict,
        msg = 'Setting parse_results = False should return a dict.')

class DtypeTests(unittest.TestCase):
    def test_steam_32_64(self):
        steam32 = 123456
        steam64 = 76561197960265728 + steam32
        account1 = entities.SteamAccount(account_id = steam64)
        account2 = entities.SteamAccount(account_id = steam32)
        self.assertEqual(account1, account2,
        'SteamAccount created with 32 Bit or 64 Bit SteamID should be indistinguishable')
    
    def test_basewrapper(self):
        obj1 = wrappers.BaseWrapper({'a':1, 'b':2, 'c':3})
        obj2 = wrappers.BaseWrapper({'a':1})
        self.assertNotEqual(obj1, obj2, f'{obj1} and {obj2} are unequal.')
        obj2['b'] = 2
        obj2['c'] = 3
        self.assertEqual(obj1['b'], 2, 'BaseWrapper __getitem__ does not work as intended.')
        with self.assertRaises(KeyError, msg = 'Trying to access non-existent properties should raise KeyError.'):
            obj1['unexpected_key']


class MatchHistoryTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_match_history = api.get_match_history
    
    def test_get_match_history_dtype(self):
        self.assertIsInstance(self.get_match_history(), wrappers.MatchHistory, 
        'get_match_history() should return a MatchHistory object')

    def test_get_match_history_hero(self):
        hero_id = 1
        hero = entities.Hero(1)
        match_hist1 = self.get_match_history(hero_id = hero_id)
        match_hist2 = self.get_match_history(hero = hero)
        self.assertEqual(match_hist1, match_hist2, 
        f'Match history called with hero = {hero} and hero_id = {hero_id} should return the same result.')
    
    def test_get_match_history_steam_account(self):
        account_id = '76561198088874284'
        steam_account = entities.SteamAccount(account_id = '76561198088874284')
        match_hist1 = self.get_match_history(account_id = account_id)
        match_hist2 = self.get_match_history(steam_account = steam_account)
        self.assertEqual(match_hist1, match_hist2,
        f'Match history called with account_id = {account_id} and steam_account = {steam_account} should return the same result.')

class MatchHistoryBySeqNumTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_match_history_by_sequence_num = api.get_match_history_by_sequence_num
    
    def test_get_match_history_by_sequence_num_dtype(self):
        self.assertIsInstance(self.get_match_history_by_sequence_num(), wrappers.MatchHistory, 
        'get_match_history_by_sequence_num() should return a MatchHistory object')

class MatchDetailsTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_match_details = api.get_match_details
    
    def test_get_match_details_dtype(self):
        match_id = '4176987886'
        self.assertIsInstance(self.get_match_details(match_id), wrappers.MatchDetails,
        f'get_match_details(\'{match_id}\') should return a MatchDetails object')

    def test_incorrect_matchid(self):
        res = self.get_match_details(match_id = 1)
        self.assertTrue(res['error'], msg = 'Incorrect match_id should have response error')
    
    def test_match_content(self):
        match_id = '4176987886'
        res = self.get_match_details(match_id)

        q = res['players_minimal'][0]['hero']
        a = entities.Hero(35)
        self.assertEqual(q, a, f'get_match_details(\'{match_id}\')[\'players_minimal\'][0][\'hero\'] is {a}')

        q = res['players'][6].all_items()[0]['item_name']
        a = 'item_tango'
        self.assertEqual(q, a, f'get_match_details(\'{match_id}\')[\'players\'][6].all_items()[0][\'item_name\'] is {a}')

        q = res['dire_buildings']['tower_status']
        a = 2047
        self.assertEqual(q, a, f'get_match_details(\'{match_id}\')[\'dire_buildings\'][\'tower_status\'] is {a}')

class HeroesTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_heroes = api.get_heroes
    
    def test_get_heroes_dtype(self):
        self.assertIsInstance(self.get_heroes(), wrappers.Heroes,
        'get_heroes() should return a Heroes object')

    def test_hero_localized_name(self):
        res = self.get_heroes(language = 'en_us')
        cur_id = 59
        cur_hero = [h for h in res['heroes'] if h['id'] == cur_id][0]
        self.assertEqual(cur_hero['localized_name'], 'Huskar',
        f'Localized name of id = {cur_id} should be Huskar')

class GameItemsTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_game_items = api.get_game_items
    
    def test_get_game_items_dtype(self):
        self.assertIsInstance(self.get_game_items(), wrappers.GameItems,
        'get_game_items() should return a GameItems object')
        
    def test_item_localized_name(self):
        res = self.get_game_items(language = 'en_us')
        cur_id = 265
        cur_item = [i for i in res['items'] if i['id'] == cur_id][0]
        self.assertEqual(cur_item['localized_name'], 'Infused Raindrops',
        f'Localized name of id = {cur_id} should be Infused Raindrops')

class TournamentPrizePoolTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_tournament_prize_pool = api.get_tournament_prize_pool
    
    def test_get_tournament_prize_pool_dtype(self):
        self.assertIsInstance(self.get_tournament_prize_pool(), wrappers.TournamentPrizePool,
        'get_tournament_prize_pool() should return a TournamentPrizePool object.')

class TopLiveGameTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_top_live_game = api.get_top_live_game
    
    def test_get_top_live_game_dtype(self):
        self.assertIsInstance(self.get_top_live_game(), wrappers.TopLiveGame,
        'get_top_live_game() should return a TopLiveGame object.')

class LanguageTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.api = api
    
    def test_wrapper_language(self):
        am_name = "敵法僧"
        lang = 'zh-TW'
        ret = self.api.get_heroes(language = lang)
        queried_am_name = [h['localized_name'] for h in ret['heroes'] if h['id'] == 1][0]
        
        self.assertEqual(queried_am_name, am_name, f'Anti-mage has the name {am_name} in {lang}')

class TeamInfoByTeamIDTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_team_info_by_team_id = api.get_team_info_by_team_id

    def test_get_team_info_by_team_id_dtype(self):
        self.assertIsInstance(self.get_team_info_by_team_id(), wrappers.TeamInfoByTeamID,
        'get_team_info_by_team_id() should return a TeamInfoByTeamID object.')

    def test_team_info_content(self):
        team_id = 46
        team_name = "Team Empire"
        time_created = 1340178158
        team_info = self.get_team_info_by_team_id(start_at_team_id = team_id)['teams'][0]

        self.assertEqual(team_info['name'], team_name, f'Team with team_id = {team_id} is {team_name}.')
        self.assertEqual(team_info['time_created'], time_created, f'Team {team_name} was created at {time_created}.')

class LiveLeagueGamesTests(unittest.TestCase):
    def setUp(self):
        api = d2api.APIWrapper()
        self.get_live_league_games = api.get_live_league_games
    
    def test_get_live_league_games_dtype(self):
        self.assertIsInstance(self.get_live_league_games(), wrappers.LiveLeagueGames,
        'get_live_league_games() should return a LiveLeagueGames object.' )

# class ArbitraryTests(unittest.TestCase):
#     def setUp(self):
#         self.api = d2api.APIWrapper()
    
#     def test_print_stuff(self):
#         print(self.api.get_match_details(4367716007))

if __name__ == '__main__':
    unittest.main()
