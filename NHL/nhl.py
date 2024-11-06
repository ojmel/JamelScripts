import math
import os
from datetime import datetime
from enum import Enum
import re

import pandas as pd
from pandasgui import show

import ScraperScripts

STATS_OF_INTEREST = {'GF/GP': 'GA/GP', 'Shots/GP': 'SA/GP', 'PP%': 'PP%'}


class Stats(Enum):
    S = 'shots-on-goal'
    P = 'points'
    A = 'assists'


player_stats = ['A', 'P', 'S']
team_ids = ScraperScripts.load_json('teams.json')
today = datetime.today().strftime("%m-%d")


class StatsManager:
    def __init__(self):
        ScraperScripts.load_html_file(f'{today}.html', 'https://www.nhl.com/stats/teams')
        self.stats = pd.read_html('test')[-1].set_index('Team')
        for offstat, defstat in STATS_OF_INTEREST.items():
            self.stats[offstat] = self.stats[offstat].rank(pct=True, ascending=True).round(2)
            self.stats[defstat] = self.stats[defstat].rank(pct=True, ascending=False).round(2)


STATS = StatsManager().stats


class MatchUpManager:
    class MatchUp:
        def __init__(self, home_name, away_name):
            self.home = ScraperScripts.word_match(home_name, STATS.index)
            self.away = ScraperScripts.word_match(away_name, STATS.index)
            self.game_table = pd.DataFrame(columns=[self.home, self.away],
                                           index=list(STATS_OF_INTEREST.keys()) + ['total'])
            self.match_sum = pd.DataFrame(columns=[self.home, self.away],
                                          index=list(STATS_OF_INTEREST.keys()) + ['total'])

        def score_match(self):
            def score_team(off_team, def_team):
                for off_stat, def_stat in STATS_OF_INTEREST.items():
                    self.game_table.loc[off_stat, off_team] = (
                    STATS.loc[off_team, off_stat], STATS.loc[def_team, def_stat])
                    self.match_sum.loc[off_stat, off_team] = ScraperScripts.subtract_all(
                        self.game_table.loc[off_stat, off_team])
                self.match_sum.loc['total', off_team] = self.game_table.loc['total', off_team] = sum(
                    self.match_sum[off_team].iloc[:-1])

            score_team(self.home, self.away)
            score_team(self.away, self.home)
            print(self.game_table)
            return self.game_table

    def __init__(self):
        self.matchups = []
        self.save_file = f'{today}.pkl'

        self.teams = []

    def create_MatchUps(self):
        games = ScraperScripts.navigable_str_to_obj(
            ScraperScripts.get_url_soup('http://sports.core.api.espn.com/v2/sports/hockey/leagues/nhl/events').contents[
                0])['items']
        game_urls = [game['$ref'] for game in games]
        for url in game_urls:
            away, home = ScraperScripts.navigable_str_to_obj(ScraperScripts.get_url_soup(url).contents[0])[
                "name"].split(
                ' at ')
            self.teams.append(home)
            self.teams.append(away)
            self.matchups.append(MatchUpManager.MatchUp(home, away))

        for match in self.matchups:
            match.score_match()
        ScraperScripts.pickle_it(self.matchups, self.save_file)
        return self.matchups

    def show_totals(self):
        if os.path.exists(self.save_file):
            matchups = ScraperScripts.unpickle_it(self.save_file)
            for match in matchups:
                print(match.game_table)
        else:
            matchups = self.create_MatchUps()
        show(pd.concat(tuple(getattr(match, 'match_sum').T for match in matchups)))


match_man = MatchUpManager()
match_man.create_MatchUps()
playing_teams = match_man.teams


class OddsManager:
    def __init__(self):
        self.player_odds = pd.DataFrame(columns=['PLAYER', 'LINE', 'ACTUAL', 'DIFF', "STAT", "MIN", "TEAMODDS", 'TEAM'])
        self.viable_players = None
        self.get_all_players()

    def get_player_odds(self, stat: Stats):
        html = f'stats/{stat.value}.html'
        ScraperScripts.load_html_file(html,
                                      r'https://sportsbook.draftkings.com/leagues/hockey/nhl?category={0}&subcategory={0}-o%2Fu'.format(
                                          stat.value))
        stat_df = pd.concat(pd.read_html(html)).drop(columns='UNDER')
        stat_df['PLAYER'] = stat_df['PLAYER'].apply(lambda player: re.sub(r'New!.*', '', player))
        stat_df['OVER'] = stat_df['OVER'].apply(
            lambda line: math.ceil(float(re.match(r'O\xa0(.+)[+−]', line).group(1))))
        stat_df.set_index('PLAYER', inplace=True)
        stat_df.rename(columns={'OVER': "LINE"}, inplace=True)
        odds = []
        for player, player_odd in stat_df.iterrows():
            if player in self.viable_players.index:
                line = player_odd['LINE']
                actual = self.viable_players.loc[player, stat.name]
                diff = actual-line
                team = ScraperScripts.word_match(self.viable_players.loc[player, 'Team'], STATS.index)
                odds.append({'PLAYER': player, 'LINE': line, 'ACTUAL': actual, 'DIFF': diff, "STAT": stat.name,
                             "TOI": self.viable_players.loc[player, 'TOI'],
                             "TEAMODDS": STATS.loc[team, 'GF/GP'] + STATS.loc[team, 'Shots/GP'], 'TEAM': team})
        return pd.DataFrame(odds)

    def get_team_players(self, team):
        html = f'teams/{team}.html'
        ScraperScripts.load_html_file(html,
                                      f'https://www.nhl.com/stats/skaters?reportType=season&seasonFrom=20242025&seasonTo=20242025&gameType=2&playerPlayedFor=franchise.{team_ids[team]}')
        team_stats = pd.read_html(html)[0].rename(columns={'TOI/GP': 'TOI'})
        team_stats['TOI'] = team_stats['TOI'].apply(lambda time: int(time.split(':')[0]))
        team_stats['Team'] = team
        team_stats = team_stats.query('TOI >= 12')
        team_stats[player_stats] = team_stats[player_stats].div(team_stats['GP'], axis=0)
        return team_stats

    def get_all_players(self):
        self.viable_players = pd.concat(self.get_team_players(team) for team in playing_teams).set_index('Player')
        return self.viable_players

    def get_all_lines(self, file):
        if os.path.exists(file):
            stats_df = pd.read_csv(file)
        else:
            stat_dfs = [self.get_player_odds(stat) for stat in Stats]
            stats_df = pd.concat(stat_dfs, ignore_index=True)
            stats_df.to_csv(file)
        return stats_df


odd_man = OddsManager()
if __name__ == '__main__':
    show(odd_man.get_all_lines(f'{today}lines.csv'))
    # MatchUpManager().show_totals()
