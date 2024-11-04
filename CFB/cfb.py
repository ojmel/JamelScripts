import json
import os.path
import pickle
from enum import Enum
import pandas as pd
import cfbd
from cfbd.rest import ApiException
from collections import defaultdict
from pandasgui import show
import difflib
from functools import reduce

from ScraperScripts import get_url_soup


class Side(Enum):
    offense = 0
    defense = 1


def subtract_all(series):
    return reduce(lambda x, y: x - y, series)


def create_game_table(off_team, def_team, team_table: pd.DataFrame, off_table, def_table):
    team_table.loc['pass', off_team] = (off_table.loc[off_team, 'PasY/G'], def_table.loc[def_team, 'PassYds/G'])
    team_table.loc['rush', off_team] = (off_table.loc[off_team, 'RusY/G'], def_table.loc[def_team, 'RushYds/G'])
    team_table.loc['pts', off_team] = (off_table.loc[off_team, 'Pts/G'], def_table.loc[def_team, 'Pts/G'])
    team_table.loc['total', off_team] = subtract_all(team_table.loc['pass', off_team]) + subtract_all(
        team_table.loc['rush', off_team]) + subtract_all(team_table.loc['pts', off_team])
    return team_table


def get_conference_stats(off_def: Side, conference):
    div, conf_id = conf_dict[conference]
    stats = get_url_soup(
        rf'https://sports.yahoo.com/ncaaf/stats/team/?selectedTable={off_def.value}&leagueStructure=ncaaf.struct.div.{div}.conf.{conf_id}')
    columns = [column.text for column in stats.find('thead').findAll('th')]
    data_table = pd.DataFrame(columns=columns)
    for team in stats.find('tbody').findAll('tr'):
        new_row = []
        for index, data in enumerate(team.findAll('td')):
            if index == 0:
                team_name: str = data.find('a', class_="C(#333)").text
                new_row.append(team_name)
                continue
            else:
                new_row.append(data.text)
        data_table = data_table._append({column: value for column, value in zip(columns, new_row)}, ignore_index=True)
    data_table = data_table.set_index('Team')
    if off_def.value:
        data_table['Pts/G'] = data_table['Pts/G'].rank(pct=True, ascending=False).round(2)
        data_table['PassYds/G'] = data_table['PassYds/G'].rank(pct=True, ascending=False).round(2)
        data_table['RushYds/G'] = data_table['RushYds/G'].rank(pct=True, ascending=False).round(2)
    else:
        data_table['Pts/G'] = data_table['Pts/G'].rank(pct=True, ascending=True).round(2)
        data_table['PasY/G'] = data_table['PasY/G'].rank(pct=True, ascending=True).round(2)
        data_table['RusY/G'] = data_table['RusY/G'].rank(pct=True, ascending=True).round(2)
    return data_table


if __name__ == '__main__':
    week = 10

    with open('smtp.json', 'rb') as jfile:
        logon_dict: dict = json.load(jfile)
    with open('conferences.json', 'rb') as jfile:
        conf_dict: dict = json.load(jfile)
    configuration = cfbd.Configuration()
    configuration.api_key['Authorization'] = logon_dict['cfb']
    configuration.api_key_prefix['Authorization'] = 'Bearer'
    api_instance = cfbd.BettingApi(cfbd.ApiClient(configuration))

    list_of_game_info = []
    if os.path.exists('data.pkl'):
        game_stats = pd.DataFrame(columns=['team', 'pass', 'rush', 'pts', 'total'])
        with open('data.pkl', 'rb') as file:  # Open a file in binary read mode
            loaded_data = pickle.load(file)  # Deserialize the object from file
        for game in loaded_data:
            print(game)
            for column in game.columns:
                team = difflib.get_close_matches(column, game.columns, n=3, cutoff=0.6)[0]
                game_stats = game_stats._append({'team': team, 'pass': subtract_all(game.loc['pass', team]),
                                                 'rush': subtract_all(game.loc['rush', team]),
                                                 'pts': subtract_all(game.loc['pts', team]),
                                                 'total': game.loc['total', team]}, ignore_index=True)
        show(game_stats)
        exit()
    try:
        stats_dict = defaultdict(dict)
        api_response = api_instance.get_lines(year=2024, week=week)
        games = [game_info for game_info in api_response if
                 game_info.away_conference == game_info.home_conference and game_info.lines]
        games = [{'home': game.home_team, 'away': game.away_team, 'conf': game.away_conference} for game in games]

        for game_info in games:
            if not stats_dict.get(game_info['conf']):
                stats_dict[game_info['conf']]['off'] = get_conference_stats(Side.offense, game_info['conf'])
                stats_dict[game_info['conf']]['def'] = get_conference_stats(Side.defense, game_info['conf'])
            offense: pd.DataFrame = stats_dict[game_info['conf']]['off']
            defense: pd.DataFrame = stats_dict[game_info['conf']]['def']
            if game_info['home'] not in offense.index:
                closest_matches = difflib.get_close_matches(game_info['home'], offense.index.to_list(), n=3, cutoff=0.5)
                home = closest_matches[0]
            else:
                home = game_info['home']

            if game_info['away'] not in offense.index:
                closest_matches = difflib.get_close_matches(game_info['away'], offense.index.to_list(), n=3, cutoff=0.5)
                away = closest_matches[0]
            else:
                away = game_info['away']

            game_table = pd.DataFrame(columns=[home, away], index=['pass', 'rush', 'pts', 'total'])
            game_table = create_game_table(home, away, game_table, offense, defense)
            game_table = create_game_table(away, home, game_table, offense, defense)

            list_of_game_info.append(game_table)
            print(game_table)

        with open('data.pkl', 'wb') as file:
            pickle.dump(list_of_game_info, file)

    except ApiException as e:
        print("Exception when calling StatsApi->get_team_season_stats: %s\n" % e)
