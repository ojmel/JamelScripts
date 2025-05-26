import re
import string
from operator import attrgetter
import numpy as np
import requests
import statsapi
import mlbstatsapi
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from numpy import mean, median
import ScraperScripts
#pip install MLB-StatsAPI

mlb = mlbstatsapi.Mlb()
runs_input={'category':'R','ascending':False}
active_columns=['team','runs','rank:Runs','opp_R(0)','LINE','SO','rank:SOs','opp_SO(0)','IP','HIP','score','side','opp']
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
    aggregate_stats['name'] = games[0].player.fullname
    aggregate_stats[
        'team'] = f'=HYPERLINK("https://www.mlb.com/player/{games[0].player.fullname.replace(" ", "-").lower()}-{pitcher_id}?stats=gamelogs-r-pitching-mlb&year=2025", "{games[-1].team.name}")'

    if games.__len__() >= num_of_games:
        games = games[-num_of_games:]
        aggregate_stats['runs'] = median(tuple(game.stat.runs for game in games))
        # TODO or weighted average
        # or find performance against closest rank
        # TODO increasing SO by when against top 10 and vice versa decreasing against bottom 10
        aggregate_stats['rank:Runs'] = {get_hit_rank_position(hit_rank, game.opponent['name'], **runs_input):game.stat.runs for game in
                                        games}
        aggregate_stats['SO'] = median(tuple(game.stat.strikeouts for game in games))
        aggregate_stats['rank:SOs'] = {get_hit_rank_position(hit_rank, game.opponent['name']):game.stat.strikeouts for game in games}
        aggregate_stats['IP'] = median(tuple(float(game.stat.inningspitched) for game in games))
        aggregate_stats['HIP'] = median(tuple(game.stat.hits for game in games)) / aggregate_stats['IP']
        aggregate_stats['score'] = aggregate_stats['SO'] + aggregate_stats['IP'] - (
                    aggregate_stats['HIP'] * aggregate_stats['runs'])
    else:
        aggregate_stats['runs'] = aggregate_stats['rank:Runs'] = np.nan
        aggregate_stats['SO'] = aggregate_stats['rank:SOs'] = np.nan
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
        # data_table.to_csv('pitch_rank.csv')
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
        # data_table.to_csv('hit_rank.csv')
        return data_table

today = datetime.now().strftime("%Y-%m-%d")
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
def pitcher_table(same_day=True):
    hit_rank = get_hitting_ranking()
    pitch_rank = get_pitch_ranking()
    pitchers=[]
    run_pots = []
    target_date= today if same_day else tomorrow
    schedule = [game for game in mlb.get_scheduled_games_by_date(start_date=target_date, end_date=target_date) if game.status.abstractgamestate!='Live']

    for game in schedule:
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
    odds=ScraperScripts.get_category_odds(ScraperScripts.Sports.baseball, ScraperScripts.BaseballCategories.pitchers,
                                           ScraperScripts.BaseballSubCategories.SOs,
                                           save_folder=r'C:\Users\jamel\PycharmProjects\JamelScripts\MLB\Data')
    pitcher_table=pd.DataFrame(pitchers).set_index('name')
    pitcher_table=pd.concat([pitcher_table,odds],axis=1)
    # pitcher_table.to_csv(f'Data\\{target_date}_todays_pitchers.csv')
    # pitcher_table=pitcher_table[~pitcher_table.index.duplicated(keep='first')]

    pitcher_table=pitcher_table[active_columns]
    for game in schedule:
        run_pot={}
        game_data = mlb.get_game(game.gamepk)
        if all(vars(game_data.gamedata.probablepitchers).values()):
            run_pot['home'] = game_data.gamedata.teams.home.name
            run_pot['away'] = game_data.gamedata.teams.away.name
            run_pot['home_pot'] = hit_rank.loc[run_pot['home'], 'R'] + mean([pitch_rank.loc[run_pot['away'], 'ER'], pitcher_table.at[game_data.gamedata.probablepitchers.away.fullname,'runs']])
            run_pot['away_pot'] = hit_rank.loc[run_pot['away'], 'R'] + mean([pitch_rank.loc[run_pot['home'], 'ER'], pitcher_table.at[game_data.gamedata.probablepitchers.home.fullname,'runs']])
            run_pot['diff'] = run_pot['home_pot']-run_pot['away_pot']
            run_pot['total']=run_pot['home_pot']+run_pot['away_pot']
            run_pots.append(run_pot)
    run_table=pd.DataFrame(run_pots)

    with pd.ExcelWriter(f"Data\\{target_date}_scores.xlsx", engine="xlsxwriter") as writer:
        pitcher_table.to_excel(writer, sheet_name="pitchers")
        run_table.to_excel(writer, sheet_name="run_pot")
        worksheet = writer.sheets["pitchers"]
        red=writer.book.add_format(({"bg_color": "red"}))
        green = writer.book.add_format(({"bg_color": "green"}))
        # Apply a conditional format to the required cell range.
        for column in ['runs','HIP']:
            excel_column=list(string.ascii_uppercase)[active_columns.index(column)+1]
            _range=f'{excel_column}2:{excel_column}{pitcher_table[column].__len__()+1}'
            worksheet.conditional_format(_range,{"type":"3_color_scale","min_color":"green",
                                           "mid_color":"yellow",
                                           "max_color":"red",
                                           "min_value":pitcher_table[column].min(),
            "max_value":pitcher_table[column].max()})
        for column in [ 'opp_R(0)', 'SO', 'opp_SO(0)', 'IP','score']:
            excel_column = list(string.ascii_uppercase)[active_columns.index(column)+1]
            _range = f'{excel_column}2:{excel_column}{pitcher_table[column].__len__() + 1}'
            worksheet.conditional_format(_range, {"type": "3_color_scale", "min_color": "red",
                                                  "mid_color": "yellow",
                                                  "max_color": "green",
                                                  "min_value": pitcher_table[column].min(),
                                                  "max_value": pitcher_table[column].max()})
        excel_column = list(string.ascii_uppercase)[active_columns.index('side')+1]
        _range = f'{excel_column}2:{excel_column}{pitcher_table["side"].__len__() + 1}'
        worksheet.conditional_format(_range, {"type": "cell", "criteria": "==", "value": '"away"', "format": red})
        worksheet.conditional_format(_range, {"type": "cell", "criteria": "==", "value": '"home"', "format": green})

    # run_table.to_csv(f'Data\\{target_date}_run_pot.csv')
    return pitcher_table

if __name__ == '__main__':
    pitcher_table()
    # import os
    # os.system(f"Data\\{today}_scores.xlsx")