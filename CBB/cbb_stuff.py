import json
import os.path
from datetime import datetime, timedelta
from enum import Enum
import re
import pandas as pd
from bs4 import BeautifulSoup
import ScraperScripts
import numpy as np
from pandasgui import show

class Pages(Enum):
    Conf = "confpage.html"
    Sched = "page.html"


stats_of_interest = ['PTS', 'REB', 'AST']
CONF_DICT = ScraperScripts.load_json(r'C:\Users\jamel\PycharmProjects\JamelScripts\CBB\cbb_espn_conf.json')
page_of_interest = Pages.Sched.value
off_url = 'https://www.espn.com/mens-college-basketball/stats/team/_/season/{year}?page={page}'
def_url = 'https://www.espn.com/mens-college-basketball/stats/team/_/view/opponent/season/{year}?page={page}'


class StatsManager:
    def get_conf_stats(self, conf_id, off_or_def='off'):
        conf_html = fr'C:\Users\jamel\PycharmProjects\JamelScripts\CBB\stats_html\{conf_id}.html'
        conf_url = off_url if off_or_def == 'off' else def_url
        if not os.path.exists(conf_html):
            ScraperScripts.load_html_file(conf_html, conf_url.format(conf_id))
        return pd.concat(pd.read_html(conf_html), axis=1).set_index('Team').drop(columns='RK')

    def get_total_stats(self, season='2025', off_or_def='off'):
        url = off_url if off_or_def == 'off' else def_url
        htmls = {
            rf'C:\Users\jamel\PycharmProjects\JamelScripts\CBB\stats_html\cbb_stats_{page}_{season}_{off_or_def}.html': url.format(
                year=season, page=page) for page in range(1, 9)}
        ScraperScripts.download_multipages(htmls)
        stat_dfs = []
        for html in htmls.keys():
            stat_dfs.append(pd.concat(pd.read_html(html), axis=1).set_index('Team').drop(columns='RK'))
        stats_df = pd.concat(stat_dfs, axis=0)
        for stat in stats_of_interest:
            stats_df[stat] = stats_df[stat].rank(pct=True, ascending=off_or_def == 'off', ).round(2)
        return stats_df


STATS = StatsManager().get_total_stats('2024')
OPP_STATS = StatsManager().get_total_stats('2024', 'def')


class MatchManager:
    class Match:
        def __init__(self, matchup_soup: BeautifulSoup):
            self.matchup_soup = matchup_soup
            away = self.matchup_soup.find('li', class_="D(tb) team")
            home = self.matchup_soup.find('li', class_="D(tb) team Pt(10px)")
            self.home_name = self.get_names(home)
            self.away_name = self.get_names(away)
            self.home = ScraperScripts.word_match(self.home_name, STATS.index, 0.7)
            self.away = ScraperScripts.word_match(self.away_name, STATS.index, 0.7)
            self.match_table = pd.DataFrame(columns=[self.home_name, self.away_name], index=stats_of_interest + ['TOT'])
            self.match_sum = pd.DataFrame(columns=[self.home_name, self.away_name],
                                          index=stats_of_interest + ['TOT']).fillna(0)
            self.parse_matchup()

        def get_names(self, team_soup):
            name = team_soup.find('span', class_="YahooSans Fw(700)! Fz(14px)!").text + ' ' + team_soup.find('div',
                                                                                                             class_="Fw(n) Fz(12px)").text
            return re.sub(r'\s*\(.*?\)\s*', ' ', name)

        def get_stat_diff(self):
            self.match_table.loc['TOT', self.home_name] = 0
            self.match_table.loc['TOT', self.away_name] = 0
            for stat in stats_of_interest:
                self.match_sum.loc[stat, self.home_name] = STATS.loc[self.home, stat] - OPP_STATS.loc[self.away, stat]
                self.match_table.loc['TOT', self.home_name] += self.match_sum.loc[stat, self.home_name]
                self.match_sum.loc['TOT', self.home_name] += self.match_sum.loc[stat, self.home_name]
                self.match_sum.loc[stat, self.away_name] = STATS.loc[self.away, stat] - OPP_STATS.loc[self.home, stat]
                self.match_table.loc['TOT', self.away_name] += self.match_sum.loc[stat, self.away_name]
                self.match_sum.loc['TOT', self.away_name] += self.match_sum.loc[stat, self.away_name]

        def parse_matchup(self):
            if self.home and self.away:
                for stat in stats_of_interest:
                    self.match_table.loc[stat, self.home_name] = (
                    STATS.loc[self.home, stat], OPP_STATS.loc[self.away, stat])
                    self.match_table.loc[stat, self.away_name] = (
                    STATS.loc[self.away, stat], OPP_STATS.loc[self.home, stat])
                self.get_stat_diff()
            else:
                del self.match_table
                del self.match_sum

    def __init__(self):
        self.matchups = []

    def get_matchups(self, date: datetime.today()):
        schedule_html = f'{date.strftime("%Y-%m-%d")}.html'
        if not os.path.exists(schedule_html):
            ScraperScripts.download_page(
                fr'https://sports.yahoo.com/college-basketball/scoreboard/?confId=all&schedState=4&dateRange={date.strftime("%Y-%m-%d")}',
                schedule_html)
        match_soups = ScraperScripts.load_html_file(schedule_html).find_all('ul', class_="Mb(3px)")
        self.matchups = [MatchManager.Match(match) for match in match_soups]
        for match in self.matchups:
            print(getattr(match, 'match_table', None))
        show(pd.concat(getattr(match, 'match_sum').T for match in self.matchups if hasattr(match, 'match_sum')))
        # if CONF_DICT.get(home) and CONF_DICT.get(away):


MatchManager().get_matchups(datetime.today())

# def get_conf_dict():
#     json_file = 'cbb_conf_dict.json'
#     if not os.path.exists(json_file):
#         conf_dict = {}
#         html_file = "confpage.html"
#         html_content = ScraperScripts.download_page('https://sports.yahoo.com/college-basketball/teams/', html_file)
#         with open(page_of_interest, "w", encoding="utf-8") as file:
#             file.write(html_file)
#         soup = BeautifulSoup(html_content, "html.parser")
#         for conf in soup.find_all('div', class_="D(ib) Pend(30px) Bxz(bb) Va(t) W(50%) Pb(40px)"):
#             conf_name = conf.find('h3').text
#             for team in conf.find_all('a',
#                                       class_="D(ib) C(primary-text) C(primary-text):link C(primary-text):visited Fz(13px) Ell"):
#                 if team_name := team.text:
#                     conf_dict[team_name] = conf_name
#         ScraperScripts.create_json(conf_dict, json_file)
#
#     else:
#         conf_dict = ScraperScripts.load_json(json_file)
#     return conf_dict
