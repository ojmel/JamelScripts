import datetime
from pathlib import Path
from googlesearch import search
from pandasgui import show
import re
import pandas as pd
import ScraperScripts
from datetime import date

"Manager is 5 for JPM Securities LLC"
"MorganStanley is 2"
change_cutoff=2
price_cutoff=40
ticker_json='StockData\\company_tickers.json'
company_name_ticker=ScraperScripts.load_json(ticker_json)

def get_tickers_with_earnings(from_date:date,to_date:date):
    base_url='https://finance.yahoo.com/calendar/earnings?from={0}&to={1}&day={2}&offset=0&size=100'
    earnings_dfs=[]
    for _date in pd.date_range(start=from_date, end=to_date).tolist():
        try:
            if _date.weekday() >= 5: continue
            url=base_url.format(from_date.strftime('%Y-%m-%d'),to_date.strftime('%Y-%m-%d'),_date.strftime('%Y-%m-%d'))
            html=f'StockData\\earnings_htmls\\{_date.strftime('%Y-%m-%d')}_earnings.html'
            ScraperScripts.load_html_file(html, url)
            earnings=pd.read_html(html)[0]
            earnings['date']=_date
            earnings_dfs.append(earnings)
        except:
            continue

    return pd.concat(earnings_dfs).set_index('Symbol')['date']

def update_tickers(company_name,ticker):
    company_name_ticker[company_name]=ticker
    ScraperScripts.create_json(company_name_ticker,ticker_json)

earning_tickers=get_tickers_with_earnings(datetime.date.today(),datetime.date.today()+datetime.timedelta(days=14))

def find_ticker(company_name):
    if ticker:=company_name_ticker.get(company_name,None):
        return ticker
    top_result=next(search(f'{company_name} yahoo ticker',pause=2,num=1,stop=1))
    print(top_result,company_name)
    try:
        ticker=re.search(r'/([^a-z]+)[/?]', top_result).group(1)
        print(ticker)
        update_tickers(company_name,ticker)
        return ticker
    except Exception as e:
        print(e)
        print(company_name+' not here')
        return None

def read_13f_filing(filing_html,other_manager=None,make_new_df=False):
    filing_csv=Path(filing_html).with_suffix('.csv')
    if filing_csv.exists() and not make_new_df:
        filing_df=pd.read_csv(filing_csv, index_col='NAME_OF_ISSUER')
    else:
        filing_df=pd.read_html(filing_html,skiprows=2,header=0)[-1]
        filing_df.columns = filing_df.columns.str.replace(' ','_')
        if other_manager: filing_df=filing_df.query(f"MANAGER == {other_manager}")
        filing_df=(filing_df.query('NAME_OF_ISSUER!="null"').query('PRN.str.startswith("SH")')
                   .set_index('NAME_OF_ISSUER',drop=True).rename(columns={'(to_the_nearest_dollar)':'value'}))

        filing_df=filing_df[['value','PRN_AMT']].groupby(filing_df.index).sum()
        filing_df['price']=filing_df['value']/filing_df['PRN_AMT']
        filing_df.query(f'price<{price_cutoff}',inplace=True)
        filing_df = filing_df[['price', 'PRN_AMT']]
        filing_df.to_csv(filing_csv)
    return filing_df

def calculate_percent_change(new_value,old_value):
    if pd.isna(new_value):
        return 0
    elif pd.isna(old_value):
        return 100
    return (new_value - old_value) / old_value * 100

def get_stock_info(ticker):
    html=ScraperScripts.load_html_file(f'StockData\\stock_htmls\\{ticker}.html',f'https://finance.yahoo.com/quote/{ticker}/')
    try:
        return {'cap':html.find('fin-streamer',{'data-field':'marketCap'}).text,'date':html.find('span',{'title':'Earnings Date'}).find_next().text}
    except:
        return {'cap':'','date':''}

def find_corporate_picks(current_filing_url, previous_filing_url, picks_csv, other_manger=None, make_new_df=False):
    if Path(picks_csv).exists() and not make_new_df:
        combined = pd.read_csv(picks_csv, index_col='NAME_OF_ISSUER')
    else:
        current_filing=f'StockData\\filings\\{current_filing_url.split('/')[-1]}'
        previous_filing = f'StockData\\filings\\{previous_filing_url.split('/')[-1]}'
        ScraperScripts.load_html_file(current_filing,current_filing_url)
        ScraperScripts.load_html_file(previous_filing, previous_filing_url)
        current_df=read_13f_filing(current_filing,other_manger,make_new_df=make_new_df).rename(columns={'PRN_AMT': "new_amount",'price':'new_price'})
        previous_df = read_13f_filing(previous_filing, other_manger,make_new_df=make_new_df).rename(columns={'PRN_AMT': "old_amount",'price':'old_price'})
        combined=pd.concat([current_df, previous_df], axis=1)
        combined['holding_change']=combined.apply(lambda row: calculate_percent_change(row['new_amount'],row['old_amount']),axis=1)
        combined.query(f'holding_change>{change_cutoff} or -{change_cutoff}>holding_change',inplace=True)
        # combined[['cap','date']]=combined.apply(lambda row: pd.Series(get_stock_info(row.name)),axis=1)
        combined.to_csv(picks_csv)
    return combined

def combine_corporations(corporation_one,corp_one_name, corporation_two,corp_two_name):
    corporation_one = corporation_one.drop(columns=['new_amount', 'old_amount']).rename(
        columns={'old_price': f'{corp_one_name}_old', 'new_price': f'{corp_one_name}_new'})
    corporation_two = corporation_two.drop(columns=['new_amount', 'old_amount']).rename(
        columns={'old_price': f'{corp_two_name}_old', 'new_price': f'{corp_two_name}_new'})
    combine_corp_df = pd.merge(corporation_one, corporation_two, left_index=True, right_index=True, how='inner').query(
        '(holding_change_x<0) == (holding_change_y<0)')
    combine_corp_df.index = [find_ticker(name) for name in combine_corp_df.index]
    combine_corp_df = pd.merge(combine_corp_df, earning_tickers, left_index=True, right_index=True, how='inner')
    combine_corp_df=combine_corp_df[combine_corp_df.index.notnull()]
    show(combine_corp_df)
    return combine_corp_df

if __name__=='__main__':
    start_over = False
    geode_picks = find_corporate_picks(
        'https://www.sec.gov/Archives/edgar/data/1214717/000121471725000012/xslForm13F_X02/GCMQ2202513F.xml',
        'https://www.sec.gov/Archives/edgar/data/1214717/000121471725000006/xslForm13F_X02/GCMQ1202513F.xml',
        'StockData\\filings\\geode_q1_q2.csv', make_new_df=start_over)
    jpm_picks = find_corporate_picks(
        'https://www.sec.gov/Archives/edgar/data/19617/000091918525000009/xslForm13F_X02/Information_Table_06.30.2025.xml',
        'https://www.sec.gov/Archives/edgar/data/19617/000001961725000443/xslForm13F_X02/Information_Table_03.31.2025.xml',
        'StockData\\filings\\jpm_q1_q2.csv', other_manger=5, make_new_df=start_over)
    morgan_picks=find_corporate_picks('https://www.sec.gov/Archives/edgar/data/895421/000089542125000499/xslForm13F_X02/US_13F-408-20250630.xml',
        'https://www.sec.gov/Archives/edgar/data/895421/000089542125000381/xslForm13F_X02/US_13F-408-20250331.xml',
        'StockData\\filings\\morgan_q1_q2.csv', other_manger=2, make_new_df=start_over)
    combine_corporations(morgan_picks,'morgan',jpm_picks,'jpm')
    combine_corporations(geode_picks, 'geode', jpm_picks, 'jpm')
    combine_corporations(morgan_picks, 'morgan', geode_picks, 'geode')
    # jpm_picks.index = [find_ticker(name) for name in jpm_picks.index]
    # jpm_picks = pd.merge(jpm_picks, earning_tickers, left_index=True, right_index=True, how='inner')
    # jpm_picks['price_change']=jpm_picks.apply(lambda row: calculate_percent_change(row['jpm_new'],row['jpm_old']),axis=1)
    # geode_picks=geode_picks.query('new_price>0.7 and new_price<3 and holding_change>0')
    # geode_picks.index = [find_ticker(name) for name in geode_picks.index]
    # geode_picks = pd.merge(geode_picks, earning_tickers, left_index=True, right_index=True, how='inner')
    # show(geode_picks)