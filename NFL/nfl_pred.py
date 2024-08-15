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
    offense = 0
    defense = 1
    special_teams = 2

    def __str__(self):
        return self.name.replace("_", "-")


side = Side.defense
stat_type = StatType.passing
year = 2023
week=1
with open('team_dict.json') as json_file:
    team_dict = json.load(json_file)


def get_team_names():
    return pd.read_csv('Teams', sep='\t', header=None)


teams = get_team_names()


def convert_html(html):
    html_str = str(html)
    return html_to_json.convert(html_str)



# def get_team_data():
#     if (response := requests.get(get_teams_data_url())).status_code == 200:
#         soup = BeautifulSoup(response.content, 'html.parser')
#         columns = [re.search(r'>(.*)<', str(column)).group(1) for column in soup.find('thead').findAll('th')]
#         data_table = pd.DataFrame(columns=columns)
#
#         for team in soup.find('tbody').findAll('tr'):
#             new_row=[]
#             for index, data in enumerate(team.findAll('td')):
#                 if index == 0:
#                     team_name=data.find('div', class_="d3-o-club-fullname").contents
#                     team_name=re.search(r'[a-zA-Z]+',team_name[0]).group(0)
#                     new_row.append(team_name)
#                     continue
#                 data=re.search(r'\d+',data.contents[0]).group(0)
#                 new_row.append(data)
#             data_table=data_table._append({column:value for column,value in zip(columns,new_row)}, ignore_index=True)
#         data_table.to_csv(f'{year}_{stat_type}_{side}.csv')
#         return data_table
#
def find_rank(sorted_dataframe:pd.DataFrame,team):
    return sorted_dataframe[sorted_dataframe['Team'] == team].index + 1

def match_up_stats(team1,team2):
    offense_stats=pd.read_csv('Offense.csv')
    offense_stats=offense_stats.sort_values('pass_average',ignore_index=True)
    team1_offpass_rank=find_rank(offense_stats,team1)
    team2_offpass_rank = find_rank(offense_stats,team2)

    offense_stats = offense_stats.sort_values('rush_average', ignore_index=True)
    team1_offrush_rank = find_rank(offense_stats,team1)
    team2_offrush_rank = find_rank(offense_stats,team2)

    offense_stats = offense_stats.sort_values('pts_average', ignore_index=True)
    team1_offpts_rank = find_rank(offense_stats, team1)
    team2_offpts_rank = find_rank(offense_stats, team2)
    team1_offpts=offense_stats[offense_stats['Team']==team1]['pts_average'].values[0]
    team2_offpts = offense_stats[offense_stats['Team'] == team2]['pts_average'].values[0]

    defense_stats=pd.read_csv('Defense.csv')
    defense_stats = defense_stats.sort_values('pass_average', ignore_index=True,ascending=False)
    team1_defpass_rank = find_rank(defense_stats, team1)
    team2_defpass_rank = find_rank(defense_stats, team2)

    defense_stats = defense_stats.sort_values('rush_average', ignore_index=True,ascending=False)
    team1_defrush_rank = find_rank(defense_stats, team1)
    team2_defrush_rank = find_rank(defense_stats, team2)

    defense_stats = defense_stats.sort_values('pts_average', ignore_index=True,ascending=False)
    team1_defpts_rank = find_rank(defense_stats, team1)
    team2_defpts_rank = find_rank(defense_stats, team2)
    team1_defpts = defense_stats[defense_stats['Team'] == team1]['pts_average'].values[0]
    team2_defpts = defense_stats[defense_stats['Team'] == team2]['pts_average'].values[0]

    team1_pass_pot=(team1_offpass_rank-team2_defpass_rank).values[0]
    team2_pass_pot=(team2_offpass_rank-team1_defpass_rank).values[0]
    team1_rush_pot=(team1_offrush_rank-team2_defrush_rank).values[0]
    team2_rush_pot=(team2_offrush_rank-team1_defrush_rank).values[0]
    team1_pts=team1_offpts+team2_defpts
    team2_pts=team2_offpts+team1_defpts
    team1_pt_pot=(team1_offpts_rank-team2_defpts_rank).values[0]
    team2_pt_pot=(team2_offpts_rank-team1_defpts_rank).values[0]

    team1_total=team1_pt_pot+team1_pass_pot+team1_rush_pot
    team2_total=team2_pass_pot+team2_rush_pot+team2_pt_pot

    print(f'\n{team1} pass:{team1_pass_pot} rush:{team1_rush_pot} pts_pot:{team1_pt_pot} pts:{team1_pts} total:{team1_total} \n'
          f'{team2} pass:{team2_pass_pot} rush:{team2_rush_pot} pts_pot:{team2_pt_pot} pts:{team2_pts} total:{team2_total}')
#
if __name__=='__main__':
    for index,game in schedule[schedule['week']==week].iterrows():
        home=team_dict[game['home_team']]
        away=team_dict[game['away_team']]
        match_up_stats(home,away)
    # team_dict = nfl.import_team_desc().set_index('team_abbr')['team_name'].to_dict()
    # with open("team_dict.json", "w") as outfile:
    #     json.dump(team_dict, outfile)

    # print(team_dict)
    # match_up_stats('Ravens', 'Chiefs')
