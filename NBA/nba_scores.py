import json
import os.path
from enum import Enum

import nba_api
import pandas as pd
from nba_api.stats.endpoints import scoreboardv2
from datetime import datetime, timedelta
from nba_api.stats.endpoints import teamyearbyyearstats
from nba_api.stats.library.parameters import SeasonTypeAllStar, MeasureTypeDetailed, PerModeSimple
from nba_api.stats.endpoints import teamdashboardbygeneralsplits, leaguedashteamstats, playerdashboardbygeneralsplits, \
    teamplayerdashboard
from pandasgui import show
from MLB.ml_pred_v3 import get_url_soup
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


def team_stats_to_csv(season='2024-25'):
    stats: pd.DataFrame = \
        leaguedashteamstats.LeagueDashTeamStats(season=season,
                                                per_mode_detailed=PerModeSimple.per_game).get_data_frames()[
            0]
    opp_stats: pd.DataFrame = \
        leaguedashteamstats.LeagueDashTeamStats(season=season, per_mode_detailed=PerModeSimple.per_game,
                                                measure_type_detailed_defense=MeasureTypeDetailed.opponent).get_data_frames()[
            0]
    for stat in stats_of_interest:
        stats[stat] = stats[stat].rank(pct=True, ascending=True).round(2)
    for stat in stats_of_interest:
        opp_stats[f'OPP_{stat}'] = opp_stats[f'OPP_{stat}'].rank(pct=True, ascending=False).round(2)
    stats.to_csv(f'nba_stats{season}.csv', index=False)
    opp_stats.to_csv(f'nba_opp_stats{season}.csv', index=False)

    return stats, opp_stats


def csv_to_stats(season='2024-25'):
    stats_file = 'nba_stats{0}.csv'.format(season)
    opp_stats_file = 'nba_opp_stats{0}.csv'.format(season)
    if not os.path.exists(stats_file) and not os.path.exists(opp_stats_file):
        team_stats_to_csv(season)

    stats = pd.read_csv(stats_file, index_col='TEAM_ID')
    opp_stats = pd.read_csv(opp_stats_file, index_col='TEAM_ID')
    return stats, opp_stats


def matchup(stats: pd.DataFrame, opp_stats, game):
    home_id = game['HOME_TEAM_ID']
    home_name = stats.loc[home_id, 'TEAM_NAME']
    away_id = game['VISITOR_TEAM_ID']
    away_name = stats.loc[away_id, 'TEAM_NAME']
    match_up = pd.DataFrame(columns=[home_name, away_name], index=stats_of_interest + ['TOT'])
    single_stat_match = pd.DataFrame(columns=[home_name, away_name], index=stats_of_interest + ['TOT', 'OPP', 'ID'])

    def score_matchup(off_id, off_name, def_id, def_name):
        for stat in stats_of_interest:
            match_up.loc[stat, off_name] = (stats.loc[off_id, stat], opp_stats.loc[def_id, f'OPP_{stat}'])
            single_stat_match.loc[stat, off_name] = stats.loc[off_id, stat] - opp_stats.loc[def_id, f'OPP_{stat}']
        single_stat_match.loc['OPP', off_name] = def_name
        single_stat_match.loc['ID', off_name] = str(off_id)

    score_matchup(home_id, home_name, away_id, away_name)
    score_matchup(away_id, away_name, home_id, home_name)
    match_up.loc['TOT', home_name] = single_stat_match.loc['TOT', home_name] = subtract_all(
        match_up.loc['PTS', home_name]) + subtract_all(
        match_up.loc['REB', home_name]) + subtract_all(match_up.loc['AST', home_name])
    match_up.loc['TOT', away_name] = single_stat_match.loc['TOT', away_name] = subtract_all(
        match_up.loc['PTS', away_name]) + subtract_all(
        match_up.loc['REB', away_name]) + subtract_all(match_up.loc['AST', away_name])
    return match_up, single_stat_match


def get_todays_games(date: datetime.date):
    matchups: list[pd.DataFrame] = []
    stats, opp_stats = team_stats_to_csv()
    stats.set_index('TEAM_ID', inplace=True)
    opp_stats.set_index('TEAM_ID', inplace=True)
    games: pd.DataFrame = scoreboardv2.ScoreboardV2(game_date=date).get_data_frames()[0]
    for row, game in games.iterrows():
        match_up, single_stat = matchup(stats, opp_stats, game)
        print(match_up)
        matchups.append(single_stat)
    return matchups


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


def get_player_stats_per_team(team_id):
    return teamplayerdashboard.TeamPlayerDashboard(team_id,
                                                   per_mode_detailed=PerModeSimple.per_game).get_data_frames()[1]


def get_total_stats(show_stats=False):
    total_stats = pd.DataFrame(columns=['Team'] + stats_of_interest + ['TOT', 'OPP'])
    matchups = get_todays_games(datetime.today())

    for match in matchups:
        for column_name, series in match.items():
            new_row = pd.DataFrame({'Team': column_name} | series.to_dict(), index=[0])
            total_stats = pd.concat([total_stats, new_row], ignore_index=True)
    if show_stats:
        show(total_stats)
    return total_stats


def get_player_odds(stat: Stats, team_name, total_stats,game_odds):
    bet_id = game_odds[team_name.replace('LA','Los Angeles')]
    player_url = f'https://api.the-odds-api.com/v4/sports/basketball_nba/events/{bet_id}/odds?apiKey={KEY}&regions=us&markets=player_{stat.value}&bookmakers=draftkings'
    team_id = total_stats.loc[total_stats['Team'] == team_name, 'ID'].values[0]
    player_stats: pd.DataFrame = get_player_stats_per_team(team_id)
    response = get_url_soup(player_url)
    stat_dicts = []
    odds_list: list[dict] = json.loads(response.contents[0])['bookmakers'][0]['markets'][0]['outcomes']

    for player_dict in odds_list:
        player_name = player_dict['description']
        if player_dict.get('name') == 'Over' and (
                real_stat := player_stats.loc[player_stats['PLAYER_NAME'] == player_name, stat.name].values):
            stat_dicts.append({'name': player_name, 'line': player_dict['point'],'stat':stat.name, 'actual': real_stat[0],
                               'odds': player_dict['price'],
                               'mins': player_stats.loc[player_stats['PLAYER_NAME'] == player_name, 'MIN'].values[0],
                               'team_odds':total_stats.loc[total_stats['Team'] == team_name,stat.name].values[0],
                               'team':team_name})
    return stat_dicts

def get_top_performers(total_stats:pd.DataFrame):
    stats_dicts=[]
    game_odds=get_gameodds_ids()
    for stat in Stats:
        top_team=total_stats.loc[total_stats[stat.name].idxmax(),'Team']
        stats_dicts=stats_dicts+get_player_odds(stat,top_team,total_stats,game_odds)
    stats_df=pd.DataFrame(stats_dicts)
    stats_df['diff']=stats_df['actual'] - stats_df['line']
    show(stats_df)


if __name__ == '__main__':
    get_top_performers(get_total_stats())
    # get_total_stats(True)

# {'name': 'Over', 'description': 'Damian Lillard', 'price': 2.14, 'point': 7.5}
# print()Index(['TEAM_ID', 'TEAM_NAME', 'GP', 'W', 'L', 'W_PCT', 'MIN', 'FGM', 'FGA',
#        'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB',
#        'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', 'PTS',
#        'PLUS_MINUS', 'GP_RANK', 'W_RANK', 'L_RANK', 'W_PCT_RANK', 'MIN_RANK',
#        'FGM_RANK', 'FGA_RANK', 'FG_PCT_RANK', 'FG3M_RANK', 'FG3A_RANK',
#        'FG3_PCT_RANK', 'FTM_RANK', 'FTA_RANK', 'FT_PCT_RANK', 'OREB_RANK',
#        'DREB_RANK', 'REB_RANK', 'AST_RANK', 'TOV_RANK', 'STL_RANK', 'BLK_RANK',
#        'BLKA_RANK', 'PF_RANK', 'PFD_RANK', 'PTS_RANK', 'PLUS_MINUS_RANK'],
#       dtype='object')
# team_dashboard = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(team_id=home,measure_type_detailed_defense=MeasureTypeDetailed.opponent,season='2023-24',per_mode_detailed=PerModeSimple.per_game).overall_team_dashboard.get_data_frame()
