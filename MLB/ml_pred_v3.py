from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import statsapi
import mlbstatsapi

from datetime import datetime, timedelta
from numpy import mean
from MLB.mlb_database import insert_game, create_db_connection, logon_dict, get_table_column
from mlb_pred_v2 import get_game_ids
def team_stats(game_id):
    game_data = statsapi.boxscore_data(game)
    home_dict={'name':game_data['teamInfo']['home']['teamName']}
    away_dict={'name':game_data['teamInfo']['away']['teamName']}

    home_id = game_data['teamInfo']['home']['id']
    away_id = game_data['teamInfo']['away']['id']
    home_stats=mlb.get_team_stats(home_id, ['season', 'seasonAdvanced'], ['hitting','pitching'],**{'season': 2024})
    away_stats=mlb.get_team_stats(away_id, ['season', 'seasonAdvanced'], ['hitting','pitching'],**{'season': 2024})
    home_hits=home_stats['hitting']['season']
    away_hits= away_stats['hitting']['season']
    home_pitch = home_stats['pitching']['season']
    away_pitch = away_stats['pitching']['season']

    home_dict['runs']=home_hits.splits[0].stat.__dict__['runs']
    away_dict['runs'] = away_hits.splits[0].stat.__dict__['runs']
    home_dict['SO']=home_hits.splits[0].stat.__dict__['strikeouts']
    away_dict['SO'] = away_hits.splits[0].stat.__dict__['strikeouts']
    home_dict['hits']=home_hits.splits[0].stat.__dict__['hits']
    away_dict['hits'] = away_hits.splits[0].stat.__dict__['hits']
    home_dict['BB'] = home_hits.splits[0].stat.__dict__['baseonballs']
    away_dict['BB'] = away_hits.splits[0].stat.__dict__['baseonballs']
    home_dict['ER'] = home_pitch.splits[0].stat.__dict__['runs']
    away_dict['ER'] = away_pitch.splits[0].stat.__dict__['runs']
    return home_dict,away_dict

mlb=mlbstatsapi.Mlb()
games=get_game_ids()
for game in games:
    home_stats,away_stats=team_stats(game)
    home_potential=home_stats['runs']+away_stats['ER']
    away_potential=away_stats['runs']+home_stats['ER']
    print(home_stats['name'],':',home_potential-away_potential,away_stats['name'],':',away_potential-home_potential)

