import json
from datetime import datetime,timedelta

from MLB.ml_pred_v3 import get_url_soup
from MLB.mlb_pred import convert_html

#gonna have to go through yahoo
response=get_url_soup(r'http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard?dates=20241104')
print(len(json.loads(response.contents[0])['events']))
# print(response.findAll('div',class_="D(ib) Pend(30px) Bxz(bb) Va(t) W(50%) Pb(40px)"))