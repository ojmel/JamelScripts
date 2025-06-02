from datetime import datetime
from pathlib import Path

from pandasgui import show
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import ScraperScripts
import pandas as pd
from selenium import webdriver
wnba_teams = {
    "ATL": "Atlanta Dream",
    "CHI": "Chicago Sky",
    "CON": "Connecticut Sun",
    "DAL": "Dallas Wings",
    "GSV": "Golden State Valkyries",
    "IND": "Indiana Fever",
    "LVA": "Las Vegas Aces",
    "LAS": "Los Angeles Sparks",
    "MIN": "Minnesota Lynx",
    "NYL": "New York Liberty",
    "PHX": "Phoenix Mercury",
    "SEA": "Seattle Storm",
    "WAS": "Washington Mystics"
}
sides=['Home','Road']
schedule_url='https://www.wnba.com/schedule?season=2025&month=all'
today = datetime.now().strftime("%Y-%m-%d")
next_game_day_info=ScraperScripts.load_html_file(f'Data\\{today}info.html', schedule_url).find_all('section', class_="GameSection_GameSection__CDIMc")[0]
game_day=next_game_day_info.find('h2', class_="GameSection_dateHeading__m5d5a").text.replace(' ', '').replace(',', '-')
games=next_game_day_info.find_all('div' ,class_="_GameTile__scoreboard_1y4oh_52")
stats_of_interest=['PTS','REB','AST']
miscellaneous_stats=['THREES']
odds_dict={ScraperScripts.Categories.PTS:ScraperScripts.SubCategories.pts,
           ScraperScripts.Categories.REB:ScraperScripts.SubCategories.rebs,
           ScraperScripts.Categories.AST:ScraperScripts.SubCategories.asts,
           ScraperScripts.Categories.THREES:ScraperScripts.SubCategories.threes}
def get_player_stats():
    stat_dfs = {}
    player_html=Path('Data').joinpath(game_day+'player_table.html')
    for side in sides:
        if not player_html.exists():
            driver = webdriver.Edge()
            driver.get('https://stats.wnba.com/players/traditional/?sort=PTS&dir=-1&Season=2025&SeasonType=Regular%20Season&LastNGames=10&Location={side}')
            dropdown = Select(driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div[2]/div/div/nba-stat-table/div[1]/div/div/select'))  # Replace with the actual ID or locator
            dropdown.select_by_visible_text("All")
            driver.implicitly_wait(5)
            html = driver.page_source
            with open(player_html, "w", encoding="utf-8") as file:
                file.write(html)
                stat_dfs[side] =pd.read_html(html, index_col='PLAYER')[0].rename(columns={'3PM':'THREES'})
        with open(player_html,'r') as file:
            stat_dfs[side] = pd.read_html(file,index_col='PLAYER')[0].rename(columns={'3PM':'THREES'})
    return stat_dfs
# TODO deal with similar names with wordmatch
def get_game_team_stats(stat_type='traditional'):
    stat_dfs={}
    for side in sides:
        html_file=f'Data\\{game_day+stat_type+side}.html'
        ScraperScripts.load_html_file(html_file,f'https://stats.wnba.com/teams/{stat_type}/?sort=W_PCT&dir=-1&Season=2025&SeasonType=Regular%20Season&LastNGames=10&Location={side}')
        with open(html_file,'r') as file:
            stat_dfs[side]=pd.read_html(file,index_col='TEAM')[0].rename(columns={("" if stat_type=='traditional' else 'Opp ')+'3PM':("" if stat_type=='traditional' else 'Opp ')+'THREES'})
    return stat_dfs


def get_matchup_table(home, away):
    team_stats = get_game_team_stats()
    table=pd.DataFrame(index=stats_of_interest+miscellaneous_stats+['TOT','side'])
    for stat in stats_of_interest+miscellaneous_stats:
        for side in sides:
            team_stats[side][stat]=team_stats[side][stat].rank(pct=True, ascending=True).round(2)
    opp_stats = get_game_team_stats('opponent')
    for stat in ['Opp '+stat for stat in stats_of_interest+miscellaneous_stats]:
        for side in sides:
            opp_stats[side][stat]=opp_stats[side][stat].rank(pct=True, ascending=False).round(2)

    def calculate_matchup(team,side,opp,opp_side):
        total=0
        matchup_dict={}
        for stat in stats_of_interest:
            matchup_dict[stat]=team_stats[side].loc[team,stat]-opp_stats[opp_side].loc[opp,'Opp '+stat]
            total+=matchup_dict[stat]
        for stat in miscellaneous_stats:
            matchup_dict[stat] = team_stats[side].loc[team, stat] - opp_stats[opp_side].loc[opp, 'Opp ' + stat]
        matchup_dict['TOT']=total
        matchup_dict['side']=side
        table[team]=pd.Series(matchup_dict)
    calculate_matchup(home,'Home',away,"Road")
    calculate_matchup(away,'Road',home,'Home')
    print(table)
    return table

def print_next_matchups(make_complete_table=True):
    matchups=[]
    for game in games:
        away,home=[team.text for team in game.find_all('p' ,class_="_TeamName__name_1k5qz_11")]
        matchups.append(get_matchup_table(home, away))
    if make_complete_table:
        return pd.concat([matchup.transpose() for matchup in matchups])

def show_player_lines(stats:list[ScraperScripts.Categories]=None):
    if stats is None:
        stats = [stat for stat in odds_dict.keys()]
    matchup_table=print_next_matchups()
    matchup_table=matchup_table.rename(columns={'3PM':'THREES'})
    odds_dfs=[]
    player_stats=get_player_stats()

    for stat in stats:
        subcat=odds_dict[stat]
        odds = ScraperScripts.get_category_odds(ScraperScripts.Sports.wnba, stat, subcat)
        for player,data in odds.iterrows():
            player_name_alt=ScraperScripts.word_match(player,get_player_stats()['Home'].index)
            odds.at[player,'TEAM']=wnba_teams[get_player_stats()['Home'].loc[player_name_alt,'TEAM']]
            side=matchup_table.loc[odds.at[player,'TEAM'],'side']
            odds.at[player, 'ACTUAL']=player_stats[side].loc[player_name_alt,stat.name]
            odds.at[player, 'LINE']=odds.loc[player,'LINE']
            odds.at[player, 'POT']=matchup_table.loc[odds.at[player,'TEAM'],stat.name]
            odds.at[player, 'STAT']=stat.name
            odds.at[player, 'MIN']=player_stats[side].loc[player_name_alt,'MIN']
        odds_dfs.append(odds)
    show(pd.concat(odds_dfs).loc[:,['TEAM','ACTUAL','LINE','POT','STAT','MIN']])

if __name__=='__main__':
    # print_next_matchups()
    show_player_lines()
