import json
import os.path
from enum import Enum

import numpy as np
import pandas as pd
import cfbd
from cfbd.rest import ApiException
from pandasgui import show
import ScraperScripts

STATS_OF_INTEREST = ['PasY/G', 'RusY/G', 'Pts/G']


class Side(Enum):
    offense = 0
    defense = 1

with open('smtp.json', 'rb') as jfile:
    LOGON_DICT: dict = json.load(jfile)
with open('conferences.json', 'rb') as jfile:
    CONF_DICT: dict = json.load(jfile)
configuration = cfbd.Configuration(
    access_token=LOGON_DICT['cfb']
)

with cfbd.ApiClient(configuration) as api_client:
    bet_api=cfbd.BettingApi(api_client)
    game_api = cfbd.GamesApi(api_client)

conf_offense_dict={}
conf_defense_dict={}

def get_conference_stats(off_def: Side, conference):
    div, conf_id = CONF_DICT[conference]

    url=rf'http://sports.yahoo.com/ncaaf/stats/team/?selectedTable={off_def.value}&leagueStructure=ncaaf.struct.div.{div}.conf.{conf_id}'
    conf_stats = pd.read_html(url)[-1].set_index('Team')
    conf_stats.rename(columns={'PassYds/G': 'PasY/G', 'RushYds/G': 'RusY/G'}, inplace=True)
    pts=conf_stats['Pts/G']
    for stat in STATS_OF_INTEREST:
        conf_stats[stat] = conf_stats[stat].rank(pct=True, ascending=(off_def.name == 'offense')).round(2)
    conf_stats['PTS']=pts
    globals()[f'conf_{off_def.name}_dict'][conference]=conf_stats
    return conf_stats
def american_to_decimal(odds):
    odds=float(odds)
    if odds<0: return (100/abs(odds))+1
    else: return (odds/100)+1

class MatchUpManager:
    """This is a manager that gets and scores intra-conference CFB games"""
    class MatchUp:
        def __init__(self, home_name, away_name, conference,lines):
            if conference in conf_offense_dict.keys():
                off_table=conf_offense_dict.get(conference)
                def_table = conf_defense_dict.get(conference)
            else:
                off_table=get_conference_stats(Side.offense, conference)
                def_table=get_conference_stats(Side.defense, conference)
            self.off_table=off_table
            self.def_table=def_table
            self.home = ScraperScripts.word_match(home_name, self.off_table.index.to_list(), 0.4)
            self.away = ScraperScripts.word_match(away_name, self.off_table.index.to_list(), 0.4)
            if self.home is None: print(home_name,self.off_table.index.to_list())
            if self.away is None: print(away_name,self.off_table.index.to_list())
            self.game_table = pd.DataFrame(columns=[self.home, self.away], index=STATS_OF_INTEREST + ['total'])
            self.match_sum = pd.DataFrame(columns=[self.home, self.away],
                                          index=STATS_OF_INTEREST + ['total'])
            self.game_table.at['odds',self.home]=american_to_decimal(lines.home_moneyline)
            self.game_table.at['spread', self.home] = lines.formatted_spread
            self.game_table.at['spread', self.away] = conference
            self.game_table.at['odds',self.away]=american_to_decimal(lines.away_moneyline)

        def score_match(self):
            def score_team(off_team, def_team):
                for stat in STATS_OF_INTEREST:
                    self.game_table.loc[stat, off_team] = (
                    self.off_table.loc[off_team, stat], self.def_table.loc[def_team, stat])
                    self.match_sum.loc[stat,off_team]=ScraperScripts.subtract_all(self.game_table.loc[stat,off_team])
                self.game_table.loc['total', off_team]=self.match_sum.loc['total', off_team] = sum(
                    (ScraperScripts.subtract_all(self.game_table.loc[stat, off_team]) for stat in STATS_OF_INTEREST))
                self.game_table.at['PTS',off_team]=np.mean((self.off_table.loc[off_team, 'PTS'], self.def_table.loc[def_team, 'PTS']))
            score_team(self.home, self.away)
            score_team(self.away, self.home)
            print(self.game_table)
            return self.game_table

    def __init__(self, week):
        self.week = week
        api_response = bet_api.get_lines(year=2025, week=week)
        games = [game_info for game_info in api_response if
                 game_info.away_conference == game_info.home_conference and game_info.lines]
        self.games = [{'home': game.home_team, 'away': game.away_team, 'conf': game.away_conference,'lines':game.lines[0]} for game in games]
        self.matchups = []
        self.save_file=f'{self.week}.pkl'

    def create_MatchUps(self):
        self.matchups=[MatchUpManager.MatchUp(match['home'], match['away'], match['conf'],match['lines']) for match in self.games]
        for match in self.matchups:
            match.score_match()
        ScraperScripts.pickle_it(self.matchups,self.save_file)
        return self.matchups

    def show_totals(self):
        if os.path.exists(self.save_file):
            matchups=ScraperScripts.unpickle_it(self.save_file)
            for match in matchups:
                print(match.game_table)
        else:
            matchups=self.create_MatchUps()
        show(pd.concat(tuple(getattr(match, 'match_sum').T for match in matchups)))


if __name__ == '__main__':
    #sort by time
    MatchUpManager(7).show_totals()

