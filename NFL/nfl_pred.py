import time
from enum import Enum

import numpy as np
# import html_to_json
import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import ScraperScripts
import nfl_data_py as nfl
from pandasgui import show

nfl_teams = {
    "ARI": "Arizona Cardinals",
    "ATL": "Atlanta Falcons",
    "BAL": "Baltimore Ravens",
    "BUF": "Buffalo Bills",
    "CAR": "Carolina Panthers",
    "CHI": "Chicago Bears",
    "CIN": "Cincinnati Bengals",
    "CLE": "Cleveland Browns",
    "DAL": "Dallas Cowboys",
    "DEN": "Denver Broncos",
    "DET": "Detroit Lions",
    "GB": "Green Bay Packers",
    "HOU": "Houston Texans",
    "IND": "Indianapolis Colts",
    "JAX": "Jacksonville Jaguars",
    "KC": "Kansas City Chiefs",
    "LV": "Las Vegas Raiders",
    "LAC": "Los Angeles Chargers",
    "LA": "Los Angeles Rams",
    "MIA": "Miami Dolphins",
    "MIN": "Minnesota Vikings",
    "NE": "New England Patriots",
    "NO": "New Orleans Saints",
    "NYG": "New York Giants",
    "NYJ": "New York Jets",
    "PHI": "Philadelphia Eagles",
    "PIT": "Pittsburgh Steelers",
    "SF": "San Francisco 49ers",
    "SEA": "Seattle Seahawks",
    "TB": "Tampa Bay Buccaneers",
    "TEN": "Tennessee Titans",
    "WAS": "Washington Commanders"
}


class StatType(Enum):
    passing = 0
    rushing = 1
    receiving = 2
    scoring = 3
    downs = 4

    def __str__(self):
        return self.name


class Side(Enum):
    offense = 'team'
    defense = 'opponent'

    def __str__(self):
        return self.name.replace("_", "-")


with open('team_dict.json') as json_file:
    team_dict = json.load(json_file)


def get_team_names():
    return pd.read_csv('Teams', sep='\t', header=None)


teams = get_team_names()
stats_of_interest = ['passing', 'rushing', 'points']


def get_schedule(year=None):
    if year is None:
        year = [2025]
    return nfl.import_schedules(year)


def get_weekly_matchup(week):
    schedule = get_schedule().query(f'week=={week}')
    match_ups = []
    for row, data in schedule.iterrows():
        match_ups.extend(match_up_stats(nfl_teams[data['home_team']], nfl_teams[data['away_team']]))
    pd.DataFrame(match_ups).to_csv(f'NFL_{week}.csv')


def get_team_data_cbs(offense_or_defense='offense'):
    data_table = \
    pd.read_html(fr'https://www.cbssports.com/nfl/stats/team/{Side[offense_or_defense].value}/total/nfl/regular/',
                 header=1)[0]
    data_table.columns = ['Team', 'GP', 'total', 'total_average', 'pass', 'pass_average', 'rush', 'rush_average', 'pts',
                          'pts_average']
    for stat in stats_of_interest:
        data_table[stat] = data_table[stat].rank(pct=True, ascending=bool(offense_or_defense == 'offense')).round(2)
    return data_table


# def get_espn_stats():
#     offense = pd.concat(pd.read_html(ScraperScripts.load_html_file('2024_Offense.html',
#                                                                    'https://www.espn.com/nfl/stats/team/_/season/2024/seasontype/2'),
#                                      header=1), axis=1)
#     offense['Baltimore Ravens'] = ['Baltimore Ravens'] + offense['Baltimore Ravens'].tolist()[:-1]
#     offense.drop(columns=['GP', 'YDS', 'YDS.1', 'YDS.2'], inplace=True)
#     offense = offense.rename(
#         columns={'Baltimore Ravens': 'Teams', 'YDS/G': 'yards', 'YDS/G.1': 'passing', 'YDS/G.2': 'rushing',
#                  'PTS/G': 'points'}).set_index('Teams')
#     offense['PTS'] = offense['points']
#     offense[stats_of_interest] = offense[stats_of_interest].apply(lambda column: column.rank(pct=True, ascending=True))
#     offense.to_csv('2024_Offense.csv')
#
#     defense = pd.concat(pd.read_html(ScraperScripts.load_html_file('2024_Defense.html',
#                                                                    'https://www.espn.com/nfl/stats/team/_/view/defense/season/2024/seasontype/2'),
#                                      header=1), axis=1)
#     defense['Philadelphia Eagles'] = ['Philadelphia Eagles'] + defense['Philadelphia Eagles'].tolist()[:-1]
#     defense.drop(columns=['GP', 'YDS', 'YDS.1', 'YDS.2'], inplace=True)
#     defense = defense.rename(
#         columns={'Philadelphia Eagles': 'Teams', 'YDS/G': 'yards', 'YDS/G.1': 'passing', 'YDS/G.2': 'rushing',
#                  'PTS/G': 'points'}).set_index('Teams')
#     defense['PTS'] = defense['points']
#     defense[stats_of_interest] = defense[stats_of_interest].apply(lambda column: column.rank(pct=True, ascending=False))
#     defense.to_csv('2024_Defense.csv')

OFF_STATS = pd.read_csv('2024_Offense.csv',index_col='Teams')
DEF_STATS = pd.read_csv('2024_Defense.csv',index_col='Teams')


def find_rank(sorted_dataframe: pd.DataFrame, team):
    return sorted_dataframe[sorted_dataframe['Team'] == team].index + 1


def match_up_stats(team1, team2):
    team1_stats = {'team': team1}
    team2_stats = {'team': team2}

    def score_team(off, defen, off_stat_dict):
        for stat in stats_of_interest:
            off_stat_dict[stat + '_potential'] = (OFF_STATS.loc[off, stat] - DEF_STATS.loc[defen, stat]).round(2)
        off_stat_dict['PTS'] = (OFF_STATS.loc[off, 'PTS']+DEF_STATS.loc[defen, 'PTS'])/2
        off_stat_dict['total'] = sum(off_stat_dict[stat + '_potential'] for stat in stats_of_interest)
        off_stat_dict['opp'] = defen

    score_team(team1, team2, team1_stats)
    score_team(team2, team1, team2_stats)
    print(team1_stats, '\n', team2_stats)
    return team1_stats, team2_stats


def get_espn_df(url, csv, number_of_scrolls=3):
    driver = webdriver.Edge()
    driver.get(url)
    time.sleep(2)
    for _ in range(number_of_scrolls):
        driver.find_element(By.XPATH,
                            '//*[@id="fittPageContainer"]/div[2]/div[2]/div/div/section/div/div[4]/div[2]/a').click()
        time.sleep(3)
    html = driver.page_source
    driver.quit()
    stat_df = pd.concat(pd.read_html(html), axis=1)
    stat_df.to_csv(csv)
    return stat_df


if __name__ == '__main__':
    # show(get_schedule())
    get_weekly_matchup(2)
    #https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2024/types/2/athletes/4036378/statistics/0?lang=en&region=us
    # test=pd.concat([pd.read_html(f"https://www.cbssports.com/nfl/stats/player/receiving/nfl/regular/qualifiers/?page={x}")[0] for x in range(1,11)])
    # test=pd.read_csv('receiver_stuff.csv')
    # print(test)
    # pandasgui.show(test)
    # test.to_csv('receiver_stuff.csv',index_label='')
    # week = 1
    # file=f'nfl_poten_{week}.csv'
    # weekly_match_up(week,file)
