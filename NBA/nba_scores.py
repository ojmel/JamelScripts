import difflib
import json
import math
import os.path
from enum import Enum
import pandas as pd
from nba_api.stats.endpoints import scoreboardv2
from datetime import datetime, timedelta
from nba_api.stats.library.parameters import SeasonTypeAllStar, MeasureTypeDetailed, PerModeSimple
from nba_api.stats.endpoints import teamdashboardbygeneralsplits, leaguedashteamstats, playerdashboardbygeneralsplits, \
    teamplayerdashboard
from pandasgui import show
from ScraperScripts import get_url_soup
from CFB.cfb import subtract_all

with open(r'C:\Users\jamel\PycharmProjects\JamelScripts\CFB\smtp.json', 'rb') as jfile:
    logon_dict: dict = json.load(jfile)
    KEY = logon_dict['odds']


class Stats(Enum):
    PTS = 'points'
    REB = 'rebounds'
    AST = 'assists'
    FG3M = 'threes'
    STL = 'steals'
    BLK = 'blocks'


stats_of_interest = [stat.name for stat in Stats]


class MatchUp:
    def __init__(self, game: pd.Series):
        self.home_id = game['HOME_TEAM_ID']
        self.home_name = STATS.loc[self.home_id, 'TEAM_NAME']
        self.away_id = game['VISITOR_TEAM_ID']
        self.away_name = STATS.loc[self.away_id, 'TEAM_NAME']
        self.info_table = pd.DataFrame(columns=[self.home_name, self.away_name], index=stats_of_interest + ['TOT'])
        self.stat_diff = pd.DataFrame(columns=[self.home_name, self.away_name],
                                      index=stats_of_interest + ['TOT', 'OPP', 'ID'])

    def score_matchup(self):
        home = self.home_name
        home_id = self.home_id
        away = self.away_name
        away_id = self.away_id
        # home
        for stat in stats_of_interest:
            self.info_table.loc[stat, home] = (STATS.loc[home_id, stat], OPP_STATS.loc[away_id, f'OPP_{stat}'])
            self.stat_diff.loc[stat, home] = STATS.loc[home_id, stat] - OPP_STATS.loc[away_id, f'OPP_{stat}']
        self.stat_diff.loc['OPP', home] = away
        self.stat_diff.loc['ID', home] = str(home_id)
        # away
        for stat in stats_of_interest:
            self.info_table.loc[stat, away] = (STATS.loc[away_id, stat], OPP_STATS.loc[home_id, f'OPP_{stat}'])
            self.stat_diff.loc[stat, away] = STATS.loc[away_id, stat] - OPP_STATS.loc[home_id, f'OPP_{stat}']
        self.stat_diff.loc['OPP', away] = home
        self.stat_diff.loc['ID', away] = str(away_id)
    def create_matchup_table(self):
        self.score_matchup()
        self.info_table.loc['TOT', self.home_name] = self.stat_diff.loc['TOT', self.home_name] = subtract_all(
            self.info_table.loc['PTS', self.home_name]) + subtract_all(
            self.info_table.loc['REB', self.home_name]) + subtract_all(self.info_table.loc['AST', self.home_name])
        self.info_table.loc['TOT', self.away_name] = self.stat_diff.loc['TOT', self.away_name] = subtract_all(
            self.info_table.loc['PTS', self.away_name]) + subtract_all(
            self.info_table.loc['REB', self.away_name]) + subtract_all(self.info_table.loc['AST', self.away_name])
        return self.info_table, self.stat_diff


class StatManager:
    def __init__(self, season='2024-25'):
        self.season = season

    def team_stats_to_csv(self):
        stats: pd.DataFrame = \
            leaguedashteamstats.LeagueDashTeamStats(season=self.season,
                                                    per_mode_detailed=PerModeSimple.per_game).get_data_frames()[
                0]
        opp_stats: pd.DataFrame = \
            leaguedashteamstats.LeagueDashTeamStats(season=self.season, per_mode_detailed=PerModeSimple.per_game,
                                                    measure_type_detailed_defense=MeasureTypeDetailed.opponent).get_data_frames()[
                0]
        for stat in stats_of_interest:
            stats[stat] = stats[stat].rank(pct=True, ascending=True).round(2)
        for stat in stats_of_interest:
            opp_stats[f'OPP_{stat}'] = opp_stats[f'OPP_{stat}'].rank(pct=True, ascending=False).round(2)
        stats.to_csv(f'nba_stats{self.season}.csv', index=False)
        opp_stats.to_csv(f'nba_opp_stats{self.season}.csv', index=False)
        stats.set_index('TEAM_ID', inplace=True)
        opp_stats.set_index('TEAM_ID', inplace=True)
        return stats, opp_stats

    def csv_to_stats(self):
        stats_file = 'nba_stats{0}.csv'.format(self.season)
        opp_stats_file = 'nba_opp_stats{0}.csv'.format(self.season)
        if not os.path.exists(stats_file) and not os.path.exists(opp_stats_file):
            self.team_stats_to_csv()
        stats = pd.read_csv(stats_file, index_col='TEAM_ID')
        opp_stats = pd.read_csv(opp_stats_file, index_col='TEAM_ID')
        return stats, opp_stats

    def get_todays_games(self, date: datetime.date=datetime.today()):
        matchups: list[pd.DataFrame] = []
        games: pd.DataFrame = scoreboardv2.ScoreboardV2(game_date=date).get_data_frames()[0]
        for row, game in games.iterrows():
            match_up, single_stat = MatchUp(game).create_matchup_table()
            print(match_up)
            matchups.append(single_stat)
        return matchups
    def get_total_stats(self, show_stats=False):
        total_stats = pd.DataFrame(columns=['Team'] + stats_of_interest + ['TOT', 'OPP'])
        matchups = self.get_todays_games(datetime.today())

        for match in matchups:
            for column_name, series in match.items():
                new_row = pd.DataFrame({'Team': column_name} | series.to_dict(), index=[0])
                total_stats = pd.concat([total_stats, new_row], ignore_index=True)
        if show_stats:
            show(total_stats)
        return total_stats


def get_gameodds_ids():
    today = datetime.today()
    tomorrow = (today + timedelta(days=1))
    h2h_url = f'https://api.the-odds-api.com/v4/sports/basketball_nba/odds/?apiKey={KEY}&regions=us&commenceTimeFrom={today.strftime("%Y-%m-%d")}T12%3A00%3A00Z&commenceTimeTo={tomorrow.strftime("%Y-%m-%d")}T12%3A00%3A00Z&markets=spreads,h2h&bookmakers=draftkings'
    response = get_url_soup(h2h_url)
    games_dict = json.loads(response.contents[0])
    bet_id_dict = {}
    for game in games_dict:
        bet_id_dict[game['home_team']] = game['id']
        bet_id_dict[game['away_team']] = game['id']
    return bet_id_dict


class OddsManager:
    def __init__(self):
        self.game_odd_ids = get_gameodds_ids()

    def get_player_stats_per_team(self,team_id):
        return teamplayerdashboard.TeamPlayerDashboard(team_id,
                                                       per_mode_detailed=PerModeSimple.per_game).get_data_frames()[
            1]

    def get_player_odds(self,stat: Stats, team_name):
        bet_name = difflib.get_close_matches(team_name, self.game_odd_ids.keys(), n=3, cutoff=0.7)[0]
        team_name=difflib.get_close_matches(team_name, TOT_STATS['Team'], n=3, cutoff=0.7)[0]
        bet_id = self.game_odd_ids[bet_name]
        player_url = f'https://api.the-odds-api.com/v4/sports/basketball_nba/events/{bet_id}/odds?apiKey={KEY}&regions=us&markets=player_{stat.value}&bookmakers=fanduel'
        team_id = TOT_STATS.loc[TOT_STATS['Team'] == team_name, 'ID'].values[0]
        player_stats: pd.DataFrame = self.get_player_stats_per_team(team_id)
        response = get_url_soup(player_url)
        stat_dicts = []
        odds_list: list[dict] = json.loads(response.contents[0])['bookmakers']
        if odds_list:
            odds_list=odds_list[0]['markets'][0]['outcomes']
            for player_dict in odds_list:
                player_name = player_dict['description']
                if player_dict.get('name') == 'Over' and (
                        real_stat := player_stats.loc[player_stats['PLAYER_NAME'] == player_name, stat.name].values):
                    line=math.ceil(player_dict['point'])
                    stat_dicts.append(
                        {'name': player_name, 'line':line , 'actual': real_stat[0],'diff':real_stat[0]-line,'stat': stat.name,
                         'odds': player_dict['price'],
                         'mins': player_stats.loc[player_stats['PLAYER_NAME'] == player_name, 'MIN'].values[0],
                         'team_odds': TOT_STATS.loc[TOT_STATS['Team'] == team_name, stat.name].values[0],
                         'team': team_name})
        return pd.DataFrame(stat_dicts)

    def get_top_performers(self):
        stat_dfs = []
        for stat in Stats:
            top_team = TOT_STATS.loc[TOT_STATS[stat.name].idxmax(), 'Team']
            stat_dfs.append(self.get_player_odds(stat, top_team))
        stats_df = pd.concat(stat_dfs,ignore_index=True)
        show(stats_df)

    def get_team_lines(self,team_name):
        stat_dfs=[]
        for stat in Stats:
            stat_dfs.append(self.get_player_odds(stat,team_name))
        stats_df = pd.concat(stat_dfs,ignore_index=True)
        return stats_df

    def get_all_lines(self,save=''):
        stat_dfs = []
        for team in self.game_odd_ids:
            stat_dfs.append(self.get_team_lines(team))
        stats_df = pd.concat(stat_dfs,ignore_index=True)
        if save:
            stats_df.to_csv(save)
        return stats_df


STATS, OPP_STATS = StatManager().team_stats_to_csv()
TOT_STATS = StatManager().get_total_stats()
if __name__ == '__main__':
    # get_top_performers(get_total_stats())
    show(TOT_STATS)
    # OddsManager().get_all_lines('todays_lines.csv')
    show(OddsManager().get_all_lines())

# {'name': 'Over', 'description': 'Damian Lillard', 'price': 2.14, 'point': 7.5}
# print()Index(['TEAM_ID', 'TEAM_NAME', 'GP', 'W', 'L', 'W_PCT', 'MIN', 'FGM', 'FGA',
#        'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB',
#        'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', 'PTS',
#        'PLUS_MINUS', 'GP_RANK', 'W_RANK', 'L_RANK', 'W_PCT_RANK', 'MIN_RANK',
#        'FGM_RANK', 'FGA_RANK', 'FG_PCT_RANK', 'FG3M_RANK', 'FG3A_RANK',
#        'FG3_PCT_RANK', 'FTM_RANK', 'FTA_RANK', 'FT_PCT_RANK', 'OREB_RANK',
#        'DREB_RANK', 'REB_RANK', 'AST_RANK', 'TOV_RANK', 'STL_RANK', 'BLK_RANK',
#        'BLKA_RANK', 'PF_RANK', 'PFD_RANK', 'PTS_RANK', 'PLUS_MINUS_RANK'],
#       dtype='object') iso_date_str = dt.isoformat() dt.replace(tzinfo=timezone.utc)
# team_dashboard = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(team_id=home,measure_type_detailed_defense=MeasureTypeDetailed.opponent,season='2023-24',per_mode_detailed=PerModeSimple.per_game).overall_team_dashboard.get_data_frame()
