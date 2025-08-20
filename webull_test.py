import pandas as pd
import ScraperScripts
import re
import pandas as pd
import ScraperScripts
from sec_cik_mapper import StockMapper
from yahoo_earnings_calendar import YahooEarningsCalendar
from datetime import date
import yahoo_fin.stock_info as si
"Manager is 5 for JPM Securities LLC"
#TODO put in market cap, change in last 3M, option prices,stock price
company_name_ticker={name.lower():ticker for ticker,name in StockMapper().ticker_to_company_name.items()}
# ScraperScripts.create_json(company_name_ticker,'company_names_vs_ticker.json')
def transform_filing_df(df,other_manager=5):
    df=df.query(f"MANAGER == {other_manager}")
    df['NAME_OF_ISSUER']=[company_name_ticker.get(ScraperScripts.word_match(name.lower(), company_name_ticker.keys(), 0.5), 'null' + name) for name in df['NAME_OF_ISSUER']]
    return df.set_index('NAME_OF_ISSUER',drop=True)

def read_13f_filing(filing_html):
    filing_df=pd.read_html(filing_html,skiprows=2,header=0)[-1]
    filing_df.columns = filing_df.columns.str.replace(' ','_')
    return transform_filing_df(filing_df.query('TITLE_OF_CLASS == "COMMON" or TITLE_OF_CLASS == "ADR"'))
def calculate_percent_change(df_row):
    if pd.isna(df_row['new_amount']):
        return 0
    elif pd.isna(df_row['old_amount']):
        return 100
    return (df_row['new_amount'] - df_row['old_amount']) / df_row['old_amount'] * 100
def get_earnings_date(from_date,to_date):
    url='https://finance.yahoo.com/calendar/earnings?from=2025-08-17&to=2025-08-23&day=2025-08-21&offset=0&size=100'
    ScraperScripts.load_html_file('test821', url)
    print(pd.read_html('test821'))

# new=read_13f_filing(r"C:\Users\jamel\Downloads\SEC FOe.html")
# new=new.groupby(new.index).sum()
# new.to_csv('630_filings_jpm.csv')
# old=read_13f_filing(r"C:\Users\jamel\Downloads\033025SECTable.html")
# old=old.groupby(old.index).sum()
# old.to_csv('330_filings_jpm.csv')
new=pd.read_csv('630_filings_jpm.csv',index_col='NAME_OF_ISSUER').rename(columns={'PRN_AMT':"new_amount"})
old=pd.read_csv('330_filings_jpm.csv',index_col='NAME_OF_ISSUER').rename(columns={'PRN_AMT':"old_amount"})
combined=pd.concat([new['new_amount'],old['old_amount']],axis=1)
combined['change']=combined.apply(calculate_percent_change,axis=1)
earnings=pd.concat([pd.read_html('test')[0],pd.read_html('test821')[0]])

print(combined.loc[[label for label in earnings['Symbol'].tolist() if label in combined.index]].sort_values('change'))
