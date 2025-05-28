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

schedule_url='https://www.wnba.com/schedule?season=2025&month=all'
today = datetime.now().strftime("%Y-%m-%d")
next_game_day_info=ScraperScripts.load_html_file(today+'test', schedule_url).find_all('section', class_="GameSection_GameSection__CDIMc")[0]
game_day=next_game_day_info.find('h2', class_="GameSection_dateHeading__m5d5a").text.replace(' ', '').replace(',', '-')
games=next_game_day_info.find_all('div' ,class_="_GameTile__scoreboard_1y4oh_52")
stats_of_interest=['PTS','REB','AST']
miscellaneous_stats=['THREES']
odds_dict={ScraperScripts.Categories.PTS:ScraperScripts.SubCategories.pts,
           ScraperScripts.Categories.REB:ScraperScripts.SubCategories.rebs,
           ScraperScripts.Categories.AST:ScraperScripts.SubCategories.asts,
           ScraperScripts.Categories.THREES:ScraperScripts.SubCategories.threes}
def get_player_stats():
    player_html=Path('Data').joinpath(game_day+'player_table.html')
    if not player_html.exists():
        driver = webdriver.Edge()
        driver.get('https://stats.wnba.com/players/traditional/?sort=PTS&dir=-1&Season=2025&SeasonType=Regular%20Season&LastNGames=10')
        dropdown = Select(driver.find_element(By.XPATH, '/html/body/main/div[2]/div/div[2]/div/div/nba-stat-table/div[1]/div/div/select'))  # Replace with the actual ID or locator
        dropdown.select_by_visible_text("All")
        driver.implicitly_wait(5)
        html = driver.page_source
        with open(player_html, "w", encoding="utf-8") as file:
            file.write(html)
            return pd.read_html(html, index_col='PLAYER')[0].rename(columns={'3PM':'THREES'})
    with open(player_html,'r') as file:
        return pd.read_html(file,index_col='PLAYER')[0].rename(columns={'3PM':'THREES'})

# TODO deal with similar names with wordmatch
def get_10_game_team_stats(stat_type='traditional'):
    html_file=f'Data\\{game_day+stat_type}.html'
    ScraperScripts.load_html_file(html_file,f'https://stats.wnba.com/teams/{stat_type}/?sort=W_PCT&dir=-1&Season=2025&SeasonType=Regular%20Season&LastNGames=10')
    with open(html_file,'r') as file:
        return pd.read_html(file,index_col='TEAM')[0].rename(columns={("" if stat_type=='traditional' else 'Opp ')+'3PM':("" if stat_type=='traditional' else 'Opp ')+'THREES'})


def matchup_table(home,away):
    team_stats = get_10_game_team_stats()
    table=pd.DataFrame(index=stats_of_interest+miscellaneous_stats+['TOT'])
    for stat in stats_of_interest+miscellaneous_stats:
        team_stats[stat]=team_stats[stat].rank(pct=True, ascending=True).round(2)
    opp_stats = get_10_game_team_stats('opponent')
    for stat in ['Opp '+stat for stat in stats_of_interest+miscellaneous_stats]:
        opp_stats[stat]=opp_stats[stat].rank(pct=True, ascending=False).round(2)
    def calculate_matchup(team,opp):
        total=0
        matchup_dict={}
        for stat in stats_of_interest:
            matchup_dict[stat]=team_stats.loc[team,stat]-opp_stats.loc[opp,'Opp '+stat]
            total+=matchup_dict[stat]
        for stat in miscellaneous_stats:
            matchup_dict[stat] = team_stats.loc[team, stat] - opp_stats.loc[opp, 'Opp ' + stat]
        matchup_dict['TOT']=total
        table[team]=pd.Series(matchup_dict)
    calculate_matchup(home,away)
    calculate_matchup(away,home)
    print(table)
    return table

def print_next_matchups(make_complete_table=True):
    matchups=[]
    for game in games:
        away,home=[team.text for team in game.find_all('p' ,class_="_TeamName__name_1k5qz_11")]
        matchups.append(matchup_table(home,away))
    if make_complete_table:
        return pd.concat([matchup.transpose() for matchup in matchups])

def show_player_lines(stats=None):
    # TODO make more clear what stat youre looking at
    if stats is None:
        stats = [stat for stat in odds_dict.keys()]
    matchup_table=print_next_matchups()
    matchup_table=matchup_table.rename(columns={'3PM':'THREES'})
    odds_dfs=[]
    for stat in stats:
        subcat=odds_dict[stat]
        odds_df = ScraperScripts.get_category_odds(ScraperScripts.Sports.wnba, stat, subcat)
        player_odds_and_stats = pd.concat([get_player_stats(), odds_df], axis=1).loc[
            list(set(odds_df.index) & set(get_player_stats().index)), ['TEAM','LINE', stat.name]].rename(columns={stat.name:'ACTUAL'})
        player_odds_and_stats['TEAM'] = player_odds_and_stats['TEAM'].apply(lambda x: wnba_teams[x])
        player_odds_and_stats['TEAM_POT']=player_odds_and_stats['TEAM'].apply(lambda team: matchup_table.loc[team,stat.name])
        player_odds_and_stats['STAT']=[stat.name]*player_odds_and_stats['TEAM'].__len__()
        odds_dfs.append(player_odds_and_stats)

    show(pd.concat(odds_dfs))

if __name__=='__main__':
    # print_next_matchups()
    show_player_lines()
