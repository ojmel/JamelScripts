import re
from operator import attrgetter

import numpy as np
import requests
import statsapi
import mlbstatsapi
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from numpy import mean, median
#pip install MLB-StatsAPI

mlb = mlbstatsapi.Mlb()
runs_input={'category':'SO','ascending':False}
def team_stats(game_id):
    game_data = statsapi.boxscore_data(game_id)
    home_dict = {'name': game_data['teamInfo']['home']['teamName'], 'side': 'home'}
    away_dict = {'name': game_data['teamInfo']['away']['teamName'], 'side': 'away'}
    for _dict in [home_dict, away_dict]:
        id = game_data['teamInfo'][_dict.get('side')]['id']
        stats = mlb.get_team_stats(id, ['season', 'seasonAdvanced'], ['hitting', 'pitching'], **{'season': 2025})
        hits = stats['hitting']['season']
        pitch = stats['pitching']['season']
        _dict['runs'] = hits.splits[0].stat.__dict__['runs']
        _dict['SO'] = hits.splits[0].stat.__dict__['strikeouts']
        _dict['hits'] = hits.splits[0].stat.__dict__['hits']
        _dict['BB'] = hits.splits[0].stat.__dict__['baseonballs']
        _dict['ER'] = pitch.splits[0].stat.__dict__['runs']
    return home_dict, away_dict

def get_pitching_lastxgames(pitcher_id, hit_rank: pd.DataFrame, num_of_games=5):
    aggregate_stats = {}

    games = mlb.get_player_stats(pitcher_id, stats=['gameLog'], groups=['pitching']).get('pitching', {}).get('gamelog',
                                                                                                             mlbstatsapi.mlb_api.Stat(
                                                                                                                 type='gameLog',
                                                                                                                 group='pitching',
                                                                                                                 totalsplits=1)).__getattribute__(
        'splits')

    if games.__len__() >= num_of_games:
        games = games[-num_of_games:]
        aggregate_stats['name'] = f'=HYPERLINK("https://www.mlb.com/player/{games[0].player.fullname.replace(" ", "-").lower()}-{pitcher_id}?stats=gamelogs-r-pitching-mlb&year=2025", "{games[0].player.fullname}")'
        aggregate_stats['team'] = games[-1].team.name
        aggregate_stats['runs'] = median(tuple(game.stat.runs for game in games))
        aggregate_stats['R_rank'] = mean(
            tuple(get_hit_rank_position(hit_rank, game.opponent['name'], **runs_input) for game in games))
        aggregate_stats['SO'] = median(tuple(game.stat.strikeouts for game in games))
        aggregate_stats['SO_rank'] = mean(
            tuple(get_hit_rank_position(hit_rank, game.opponent['name']) for game in games))
        aggregate_stats['IP'] = median(tuple(float(game.stat.inningspitched) for game in games))
        aggregate_stats['HIP'] = median(tuple(game.stat.hits for game in games)) / aggregate_stats['IP']
        aggregate_stats['score'] = aggregate_stats['SO'] + aggregate_stats['IP'] - (
                    aggregate_stats['HIP'] * aggregate_stats['runs'])
    else:
        aggregate_stats['name'] =  f'=HYPERLINK("https://www.mlb.com/player/{games[0].player.fullname.replace(" ", "-").lower()}-{pitcher_id}?stats=gamelogs-r-pitching-mlb&year=2025", "{games[0].player.fullname}")'
        aggregate_stats['team'] = games[-1].team.name if games[-1].team.name else ''
        aggregate_stats['runs'] = aggregate_stats['R_rank'] = np.nan
        aggregate_stats['SO'] = aggregate_stats['SO_rank'] = np.nan
        aggregate_stats['HIP'] = aggregate_stats['IP'] = np.nan
        aggregate_stats['score'] = np.nan
    return aggregate_stats


# game.__getattribute__('ishome') game_data.gamedata.teams.away.name
# # Loop through the games to find starting pitchers

def get_hit_rank_position(hit_rank: pd.DataFrame, team: str, category='SO',ascending=True):
    # Runs are ascending False
    hit_rank = hit_rank.sort_values(category,ascending=ascending)
    return hit_rank.index.get_loc(team)


def get_pitch_ranking():
    stat_url = 'https://www.mlb.com/stats/team/pitching?timeframe=-29'
    if (response := requests.get(stat_url)).status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        seen_set = set()
        columns = []
        for column in soup.find('thead').findAll('abbr'):
            column = re.search(r'>(.*)<', str(column)).group(1)
            if column not in seen_set:
                columns.append(column)
                seen_set.add(column)
        data_table = pd.DataFrame(columns=columns)
        for team in soup.find('tbody').findAll('tr'):
            new_row = []
            team_name = team.find('th').find('a')['aria-label']
            new_row.append(team_name)
            for stat in team.findAll('td'):
                new_row.append(stat.text)
            data_table = data_table._append({column: value for column, value in zip(columns, new_row)},
                                            ignore_index=True)
        data_table = data_table.set_index('TEAM').infer_objects()
        data_table['ER'] = data_table['ER'].astype(int) / data_table['G'].astype(int)
        data_table.to_csv('pitch_rank.csv')
        data_table = pd.read_csv('pitch_rank.csv', index_col='TEAM')
        return data_table


def get_hitting_ranking():
    stat_url = 'https://www.mlb.com/stats/team?timeframe=-29'

    if (response := requests.get(stat_url)).status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        seen_set = set()
        columns = []
        for column in soup.find('thead').findAll('abbr'):
            column = re.search(r'>(.*)<', str(column)).group(1)
            if column not in seen_set:
                columns.append(column)
                seen_set.add(column)
        data_table = pd.DataFrame(columns=columns)
        for team in soup.find('tbody').findAll('tr'):
            new_row = []
            team_name = team.find('th').find('a')['aria-label']
            new_row.append(team_name)
            for stat in team.findAll('td'):
                new_row.append(stat.text)
            data_table = data_table._append({column: value for column, value in zip(columns, new_row)},
                                            ignore_index=True)
        data_table = data_table.set_index('TEAM')
        data_table['R'] = data_table['R'].astype(int) / data_table['G'].astype(int)
        data_table.to_csv('hit_rank.csv')
        data_table = pd.read_csv('hit_rank.csv', index_col='TEAM')
        return data_table


def pitcher_table(same_day=True):
    hit_rank = get_hitting_ranking()
    pitch_rank = get_pitch_ranking()
    pitchers=[]
    run_pots = []
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    target_date= today if same_day else tomorrow
    schedule = mlb.get_scheduled_games_by_date(start_date=target_date, end_date=target_date)

    for game in schedule:
        if game.status.abstractgamestate!='Live':

            game_data = mlb.get_game(game.gamepk)
            away_name = game_data.gamedata.teams.away.name
            home_name = game_data.gamedata.teams.home.name
            for side,pitcher in vars(game_data.gamedata.probablepitchers).items():
                if pitcher:
                    opp= home_name if side=='away' else away_name
                    pitcher_stats = get_pitching_lastxgames(pitcher.id, hit_rank)
                    pitcher_stats['side'] = side
                    pitcher_stats['opp'] = opp
                    pitcher_stats['opp_SO(0)'] = get_hit_rank_position(hit_rank, opp)
                    pitcher_stats['opp_R(0)'] = get_hit_rank_position(hit_rank, opp, **runs_input)
                    pitchers.append(pitcher_stats)
    pitcher_table=pd.DataFrame(pitchers).set_index('team')
    pitcher_table.to_csv(f'Data\\{target_date}_todays_pitchers.csv')
    pitcher_table=pitcher_table[~pitcher_table.index.duplicated(keep='first')]

    for game in schedule:
        if game.status.abstractgamestate!='Live':
            run_pot={}
            game_data = mlb.get_game(game.gamepk)
            if all(vars(game_data.gamedata.probablepitchers).values()):
                run_pot['home'] = game_data.gamedata.teams.home.name
                run_pot['away'] = game_data.gamedata.teams.away.name
                run_pot['home_pot'] = hit_rank.loc[run_pot['home'], 'R'] + mean([pitch_rank.loc[run_pot['away'], 'ER'], pitcher_table.at[run_pot['away'],'runs']])
                run_pot['away_pot'] = hit_rank.loc[run_pot['away'], 'R'] + mean([pitch_rank.loc[run_pot['home'], 'ER'], pitcher_table.at[run_pot['home'],'runs']])
                run_pot['diff'] = run_pot['home_pot']-run_pot['away_pot']
                run_pot['total']=run_pot['home_pot']+run_pot['away_pot']
                run_pots.append(run_pot)
    run_table=pd.DataFrame(run_pots)
    run_table.to_csv(f'Data\\{target_date}_run_pot.csv')

    return pitcher_table

if __name__ == '__main__':
    pitcher_table(False)
