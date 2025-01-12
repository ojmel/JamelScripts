from enum import Enum
import html_to_json
import pandas as pd
import json
from pandasgui import show
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
    data_table=pd.read_html(fr'https://www.cbssports.com/nfl/stats/team/{Side[offense_or_defense].value}/total/nfl/regular/',header=1)[0]
    data_table.columns=['Team', 'GP', 'total', 'total_average', 'pass', 'pass_average', 'rush', 'rush_average', 'pts', 'pts_average']
    for stat in stats_of_interest:
        data_table[stat]=data_table[stat].rank(pct=True, ascending=bool(offense_or_defense == 'offense')).round(2)
    return data_table


OFF_STATS=get_team_data_cbs('offense')
OFF_STATS.index=[x.replace(' ','') for x in OFF_STATS['Team']]
DEF_STATS= get_team_data_cbs('defense')
DEF_STATS.index = [x.replace(' ', '') for x in DEF_STATS['Team']]


def find_rank(sorted_dataframe:pd.DataFrame,team):
    return sorted_dataframe[sorted_dataframe['Team'] == team].index + 1


def match_up_stats(team1,team2):
    team1=team1.replace(' ','')
    team2=team2.replace(' ','')
    team1_stats={'team':team1}
    team2_stats={'team':team2}

    def score_team(off, defen, off_stat_dict):
        for stat in stats_of_interest:
            off_stat_dict[stat]=(OFF_STATS.loc[off,stat] - DEF_STATS.loc[defen,stat]).round(2)
        offpts=(OFF_STATS.loc[off,'pts']/OFF_STATS.loc[off,'GP']).round(2)
        defpts = (DEF_STATS.loc[defen,'pts']/DEF_STATS.loc[defen,'GP']).round(2)
        off_stat_dict['pts']=round((float(offpts) + float(defpts)) / 2, 2)
        off_stat_dict['total']=sum(off_stat_dict[stat] for stat in stats_of_interest).round(2)
        off_stat_dict['opp'] =defen

    score_team(team1,team2,team1_stats)
    score_team(team2, team1, team2_stats)
    print(team1_stats,'\n',team2_stats)
    return team1_stats,team2_stats


if __name__=='__main__':
    week = 16
    year = 2024
    team_potential=[]
    for index,game in schedule[schedule['week']==week].iterrows():
        home=team_dict[game['home_team']]
        away=team_dict[game['away_team']]
        home_dict,away_dict=match_up_stats(home,away)
        team_potential.append(home_dict)
        team_potential.append(away_dict)
    team_potential=pd.DataFrame(team_potential)
    team_potential.to_csv(f'nfl_poten_{week}.csv')

