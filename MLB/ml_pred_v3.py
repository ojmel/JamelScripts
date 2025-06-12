import re
import string
from operator import attrgetter
from pathlib import Path

import numpy as np
import requests
import statsapi
import mlbstatsapi
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
from numpy import mean, median
import ScraperScripts
from unidecode import unidecode

#pip install MLB-StatsAPI

mlb = mlbstatsapi.Mlb()
runs_input = {'category': 'runs', 'ascending': False}
active_columns = ['team', 'runs', 'rank:Runs', 'opp_R(0)', 'LINE','SO', 'rank:SOs', 'opp_SO(0)', 'IP', 'HIP', 'score',
                  'side', 'opp']

mlb_teams = {
    "Atlanta Braves": 144,
    "Arizona Diamondbacks": 109,
    "Baltimore Orioles": 110,
    "Boston Red Sox": 111,
    "Chicago White Sox": 145,
    "Chicago Cubs": 112,
    "Cincinnati Reds": 113,
    "Cleveland Guardians": 114,
    "Colorado Rockies": 115,
    "Detroit Tigers": 116,
    "Houston Astros": 117,
    "Kansas City Royals": 118,
    "Los Angeles Angels": 108,
    "Los Angeles Dodgers": 119,
    "Miami Marlins": 146,
    "Milwaukee Brewers": 158,
    "Minnesota Twins": 142,
    "New York Yankees": 147,
    "New York Mets": 121,
    "Oakland Athletics": 133,
    "Philadelphia Phillies": 143,
    "Pittsburgh Pirates": 134,
    "San Diego Padres": 135,
    "San Francisco Giants": 137,
    "Seattle Mariners": 136,
    "St. Louis Cardinals": 138,
    "Tampa Bay Rays": 139,
    "Texas Rangers": 140,
    "Toronto Blue Jays": 141,
    "Washington Nationals": 120
}

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


def get_pitching_lastxgames(pitcher_id, hit_rank: dict[str,pd.DataFrame], num_of_games=5):
    aggregate_stats = {}
    games = mlb.get_player_stats(pitcher_id, stats=['gameLog'], groups=['pitching']).get('pitching', {}).get('gamelog',
                                                                                                             mlbstatsapi.mlb_api.Stat(
                                                                                                                 type='gameLog',
                                                                                                                 group='pitching',
                                                                                                                 totalsplits=1)).__getattribute__(
        'splits')
    aggregate_stats['name'] = unidecode(mlb.get_person(pitcher_id).fullname.replace('.',''))
    if games.__len__() >= num_of_games:
        games = games[-num_of_games:]
        aggregate_stats[
            'team'] = f'=HYPERLINK("https://www.mlb.com/player/{aggregate_stats["name"].replace(" ", "-").lower()}-{pitcher_id}?stats=gamelogs-r-pitching-mlb&year=2025", "{games[-1].team.name}")'
        aggregate_stats['runs'] = median(tuple(game.stat.runs for game in games))
        # TODO or weighted average
        # or find performance against closest rank
        # TODO increasing SO by when against top 10 and vice versa decreasing against bottom 10
        aggregate_stats['rank:Runs'] = {
            ('h' if game.ishome else 'a')+str(get_team_rank(hit_rank['away' if game.ishome else 'home'], game.opponent['name'], **runs_input)): game.stat.runs for game in
            games}
        aggregate_stats['SO'] = median(tuple(game.stat.strikeouts for game in games))
        aggregate_stats['rank:SOs'] = {('h' if game.ishome else 'a')+str(get_team_rank(hit_rank['away' if game.ishome else 'home'], game.opponent['name'])): game.stat.strikeouts for
                                       game in games}
        aggregate_stats['IP'] = median(tuple(float(game.stat.inningspitched) for game in games))
        aggregate_stats['HIP'] = median(tuple(game.stat.hits for game in games)) / aggregate_stats['IP']
        aggregate_stats['score'] = aggregate_stats['SO'] + aggregate_stats['IP'] - (
                aggregate_stats['HIP'] * aggregate_stats['runs'])
    else:

        aggregate_stats['team'] = f'=HYPERLINK("https://www.mlb.com/player/{aggregate_stats["name"].replace(" ", "-").lower()}-{pitcher_id}?stats=gamelogs-r-pitching-mlb&year=2025", "Short")'
        aggregate_stats['runs'] = aggregate_stats['rank:Runs'] = None
        aggregate_stats['SO'] = aggregate_stats['rank:SOs'] = None
        aggregate_stats['HIP'] = aggregate_stats['IP'] = None
        aggregate_stats['score'] = None
    return aggregate_stats


# game.__getattribute__('ishome') game_data.gamedata.teams.away.name
# # Loop through the games to find starting pitchers

def get_team_rank(hit_rank: pd.DataFrame, team: str, category='strikeOuts', ascending=True):
    # Runs are ascending False
    hit_rank = hit_rank.sort_values(category, ascending=ascending)
    return hit_rank.index.get_loc(team)


def get_team_stats(stats_of_interest=None, stat_type='pitching'):
    if stats_of_interest is None:
        stats_of_interest = ['runs']
    end = datetime.now().strftime("%Y-%m-%d")
    start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if (json_file:=Path('Data').joinpath(f'{end+stat_type}_info.json')).exists():
        team_games =ScraperScripts.load_json(json_file)
    else:
        team_games = {team: requests.get(url='https://statsapi.mlb.com/api/v1/teams/{team_id}'
                                             '/stats?stats=gamelog&group={stat_type}&startDate={start}&endDate={end}'
                                         .format(team_id=_id, start=start, end=end,stat_type=stat_type)).json() for team, _id in mlb_teams.items()}
        ScraperScripts.create_json(team_games,json_file)
    def pool_stats(side):
        total_team_stats = []
        for team, stat_json in team_games.items():
            stat_dict = {'team': team}
            games = stat_json.get('stats')[0].get('splits')
            for stat in stats_of_interest:
                stat_dict[stat] = mean([game['stat'][stat] for game in games if game.get('isHome') == (side == 'home')])
            total_team_stats.append(stat_dict)
        return pd.DataFrame(total_team_stats).set_index('team')

    return {side:pool_stats(side) for side in ['home', 'away']}


today = datetime.now().strftime("%Y-%m-%d")
tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

def pitcher_table(same_day=True):
    hit_rank = get_team_stats(['runs','strikeOuts'],'hitting')
    pitch_rank = get_team_stats()
    pitchers = []
    run_pots = []
    target_date = today if same_day else tomorrow
    schedule = [game for game in mlb.get_scheduled_games_by_date(start_date=target_date, end_date=target_date) if
                game.status.abstractgamestate != 'Live']

    for game in schedule:
        game_data = mlb.get_game(game.gamepk)
        away_name = game_data.gamedata.teams.away.name
        home_name = game_data.gamedata.teams.home.name
        for side, pitcher in vars(game_data.gamedata.probablepitchers).items():
            if pitcher:
                opp = home_name if side == 'away' else away_name
                opp_side= 'home' if side == 'away' else 'away'
                pitcher_stats = get_pitching_lastxgames(pitcher.id, hit_rank)
                pitcher_stats['side'] = side
                pitcher_stats['opp'] = opp
                pitcher_stats['opp_SO(0)'] = get_team_rank(hit_rank[opp_side], opp)
                pitcher_stats['opp_R(0)'] = get_team_rank(hit_rank[opp_side], opp, **runs_input)
                pitchers.append(pitcher_stats)
    odds = ScraperScripts.get_category_odds(ScraperScripts.Sports.mlb, ScraperScripts.Categories.pitchers,
                                            ScraperScripts.SubCategories.SOs,target_date,
                                            save_folder=r'C:\Users\jamel\PycharmProjects\JamelScripts\MLB\Data')

    pitcher_df = pd.DataFrame(pitchers).set_index('name')
    pitcher_df = pd.concat([pitcher_df, odds], axis=1)
    pitcher_df = pitcher_df[active_columns]

    for game in schedule:
        run_pot = {}
        game_data = mlb.get_game(game.gamepk)
        for side, pitcher in vars(game_data.gamedata.probablepitchers).items():
            opp_side = 'home' if side == 'away' else 'away'
            team=attrgetter(f"{side}.name")(game_data.gamedata.teams)
            opp =attrgetter(f"{opp_side}.name")(game_data.gamedata.teams)
            run_pot[side] = attrgetter(f"{side}.name")(game_data.gamedata.teams)
            run_pot[side+'_pot'] =[hit_rank[side].loc[team, 'runs'], pitch_rank[opp_side].loc[opp, 'runs']]
            if attrgetter(f"{opp_side}")(game_data.gamedata.probablepitchers):
                opp_pitcher =unidecode(attrgetter(f"{opp_side}.fullname")(game_data.gamedata.probablepitchers))
                opp_pitcher =ScraperScripts.word_match(opp_pitcher,pitcher_df.index)
                if (pitch_er :=pitcher_df.at[opp_pitcher, 'runs']) is not np.nan and pitcher_df.at[opp_pitcher, 'IP']>=3.0:
                    run_pot[side+'_pot'] += [pitch_er]
            run_pot[side+'_pot']=mean(run_pot[side+'_pot'])
        run_pot['diff'] = run_pot['home_pot'] - run_pot['away_pot']
        run_pot['total'] = run_pot['home_pot'] + run_pot['away_pot']
        run_pots.append(run_pot)
    run_table = pd.DataFrame(run_pots)[['home','away','home_pot','away_pot','diff','total']].set_index('home')

    with pd.ExcelWriter(f"Data\\{target_date}_scores.xlsx", engine="xlsxwriter") as writer:
        pitcher_df.to_excel(writer, sheet_name="pitchers")
        run_table.to_excel(writer, sheet_name="run_pot")
        worksheet = writer.sheets["pitchers"]
        red = writer.book.add_format(({"bg_color": "red"}))
        green = writer.book.add_format(({"bg_color": "green"}))

        for column in ['runs', 'HIP']:
            excel_column = list(string.ascii_uppercase)[active_columns.index(column) + 1]
            _range = f'{excel_column}2:{excel_column}{pitcher_df[column].__len__() + 1}'
            worksheet.conditional_format(_range, {"type": "3_color_scale", "min_color": "green",
                                                  "mid_color": "yellow",
                                                  "max_color": "red",
                                                  "min_value": pitcher_df[column].min(),
                                                  "max_value": pitcher_df[column].max()})
        for column in ['opp_R(0)', 'SO', 'opp_SO(0)', 'IP', 'score']:
            excel_column = list(string.ascii_uppercase)[active_columns.index(column) + 1]
            _range = f'{excel_column}2:{excel_column}{pitcher_df[column].__len__() + 1}'
            worksheet.conditional_format(_range, {"type": "3_color_scale", "min_color": "red",
                                                  "mid_color": "yellow",
                                                  "max_color": "green",
                                                  "min_value": pitcher_df[column].min(),
                                                  "max_value": pitcher_df[column].max()})
        excel_column = list(string.ascii_uppercase)[active_columns.index('side') + 1]
        _range = f'{excel_column}2:{excel_column}{pitcher_df["side"].__len__() + 1}'
        worksheet.conditional_format(_range, {"type": "cell", "criteria": "==", "value": '"away"', "format": red})
        worksheet.conditional_format(_range, {"type": "cell", "criteria": "==", "value": '"home"', "format": green})

    return pitcher_df,run_table


if __name__ == '__main__':
    _,runpot=pitcher_table()
    import os
    # TODO make this better over the last 15-20 games and put in master list with team name and opposing pitcher
    print('Home')
    for team in runpot.index:
        print(team)
        print(pd.read_html(rf'https://www.mlb.com/orioles/stats/{team.lower().replace(" ","-").replace(".","")}/hits?split=h')[0].set_index('PLAYERPLAYER').rename(columns={'caret-upcaret-downHcaret-upcaret-downH':'H'})[['H','ABAB','RR','SOSO','RBIRBI','AVGAVG']])
    print('Away')
    for team in runpot['away']:
        print(team)
        print(pd.read_html(rf'https://www.mlb.com/orioles/stats/{team.lower().replace(" ","-")}/hits?split=a')[0].set_index('PLAYERPLAYER').rename(columns={'caret-upcaret-downHcaret-upcaret-downH':'H'})[['H','ABAB','RR','SOSO','RBIRBI','AVGAVG']])
    os.system(f"Data\\{today}_scores.xlsx")
