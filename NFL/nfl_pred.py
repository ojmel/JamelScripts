#Could buildnew data from rosster instead of relying on 2023 import_schedules()
import re
from enum import Enum
import html_to_json
import pandas as pd
import requests
import json
import nfl_data_py as nfl
from bs4 import BeautifulSoup

schedule=pd.read_csv('2024_schedule.csv')
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
stats_of_interest = ['pass_average', 'rush_average','pts_average']

def convert_html(html):
    html_str = str(html)
    return html_to_json.convert(html_str)


def get_team_data_cbs(offense_or_defense='offense'):
    if (response := requests.get(fr'https://www.cbssports.com/nfl/stats/team/{Side[offense_or_defense].value}/total/nfl/regular/')).status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        columns =['Team', 'GP', 'total', 'total_average', 'pass', 'pass_average', 'rush', 'rush_average', 'pts', 'pts_average']
        data_table = pd.DataFrame(columns=columns)
        for team in soup.find('tbody').findAll('tr'):
            new_row=[]
            for index,data in enumerate(team.findAll('td')):
                if index==0:
                    new_row.append(str(re.search(r'[\w.\s/]+',data.text).group(0)))
                else:
                    new_row.append(float(re.search(r'[\w./]+', data.text).group(0)))
            data_table=data_table._append({column:value for column,value in zip(columns,new_row)}, ignore_index=True)
        for stat in stats_of_interest:
            data_table[stat]=data_table[stat].rank(pct=True, ascending=bool(offense_or_defense == 'offense')).round(2)
        return data_table

def find_rank(sorted_dataframe:pd.DataFrame,team):
    return sorted_dataframe[sorted_dataframe['Team'] == team].index + 1


def match_up_stats(team1,team2):
    team1=team1.replace(' ','')
    team2=team2.replace(' ','')
    offense_stats=get_team_data_cbs('offense')
    offense_stats.index=[x.replace(' ','') for x in offense_stats['Team']]
    team1_offpass_rank=offense_stats.loc[team1,'pass_average']
    team2_offpass_rank = offense_stats.loc[team2,'pass_average']

    team1_offrush_rank = offense_stats.loc[team1,'rush_average']
    team2_offrush_rank = offense_stats.loc[team2,'rush_average']

    team1_offpts_rank = offense_stats.loc[team1,'pts_average']
    team2_offpts_rank = offense_stats.loc[team2,'pts_average']
    team1_offpts=offense_stats.loc[team1,'pts']/offense_stats.loc[team1,'GP']
    team2_offpts = offense_stats.loc[team2,'pts']/offense_stats.loc[team2,'GP']

    defense_stats=get_team_data_cbs('defense')
    defense_stats.index = [x.replace(' ', '') for x in defense_stats['Team']]

    team1_defpass_rank = defense_stats.loc[team1,'pass_average']
    team2_defpass_rank = defense_stats.loc[team2,'pass_average']

    team1_defrush_rank = defense_stats.loc[team1,'rush_average']
    team2_defrush_rank = defense_stats.loc[team2,'rush_average']

    team1_defpts_rank = defense_stats.loc[team1,'pts_average']
    team2_defpts_rank = defense_stats.loc[team2,'pts_average']
    team1_defpts = defense_stats.loc[team1,'pts']/defense_stats.loc[team1,'GP']
    team2_defpts = defense_stats.loc[team2,'pts']/defense_stats.loc[team2,'GP']

    team1_pass_pot=(team1_offpass_rank-team2_defpass_rank).round(2)
    team2_pass_pot=(team2_offpass_rank-team1_defpass_rank).round(2)
    team1_rush_pot=(team1_offrush_rank-team2_defrush_rank).round(2)
    team2_rush_pot=(team2_offrush_rank-team1_defrush_rank).round(2)
    team1_pts=round((float(team1_offpts)+float(team2_defpts))/2,2)
    team2_pts=round((float(team2_offpts)+float(team1_defpts))/2,2)
    team1_pt_pot=(team1_offpts_rank-team2_defpts_rank).round(2)
    team2_pt_pot=(team2_offpts_rank-team1_defpts_rank).round(2)

    team1_total=(team1_pt_pot+team1_pass_pot+team1_rush_pot).round(2)
    team2_total=(team2_pass_pot+team2_rush_pot+team2_pt_pot).round(2)

    print(f'\n{team1} pass:{team1_pass_pot} rush:{team1_rush_pot} pts_pot:{team1_pt_pot} pts:{team1_pts} total:{team1_total} \n'
          f'{team2} pass:{team2_pass_pot} rush:{team2_rush_pot} pts_pot:{team2_pt_pot} pts:{team2_pts} total:{team2_total}')
    return {'team':team1, 'pass':team1_pass_pot, 'rush':team1_rush_pot, 'pts_pot':team1_pt_pot, 'pts':team1_pts, 'total':team1_total,'opp':team2},\
    {'team':team2, 'pass':team2_pass_pot, 'rush':team2_rush_pot, 'pts_pot':team2_pt_pot, 'pts':team2_pts, 'total':team2_total,'opp':team1}

if __name__=='__main__':
    week = 9
    year = 2024
    team_potential=pd.DataFrame()
    for index,game in schedule[schedule['week']==week].iterrows():
        home=team_dict[game['home_team']]
        away=team_dict[game['away_team']]
        home_dict,away_dict=match_up_stats(home,away)
        team_potential=team_potential._append(home_dict,ignore_index=True)
        team_potential = team_potential._append(away_dict,ignore_index=True)
    team_potential.to_csv(f'nfl_poten_{week}.csv')

