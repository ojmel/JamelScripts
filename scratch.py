import time

import numpy as np
import pandas as pd
from pandasgui import show
import yfinance as yf

tickers = pd.read_csv(r"C:\Users\jamel\Downloads\ExportTable.csv", index_col='Symbol')
tickers['diff_to_low'] = ((tickers['Last'] - tickers['52 Week Low']) / tickers['52 Week Low']) * 100
tickers=tickers.sort_values(by='Percent Average Call Volume',ascending=False).query("diff_to_low<50 and Sector not in ['Financials','Real Estate']")
def get_call_options(ticker) -> pd.DataFrame:
    time.sleep(1)
    stock = yf.Ticker(ticker)
    # Fetch options expiration dates
    expirations = stock.options
    print("Available Expiration Dates:", expirations)
    if expirations:
        expiration_date = expirations[1]  # Example: First expiration date
        options_chain = stock.option_chain(expiration_date)

        # Separate calls and puts
        return options_chain.calls

for index,ticker in enumerate(tickers.index[:]):
    calls=get_call_options(ticker)
    differences = np.abs(calls['strike'] - tickers.loc[ticker,'Last'])
    nearest_indices = differences.argsort()[:2]
    nearest_calls = calls.iloc[nearest_indices]
    nearest_calls['price']=tickers.loc[ticker,'Last']
    nearest_calls['Sector']=tickers.loc[ticker,'Sector']
    if (nearest_calls['lastPrice']<0.3).any():
        show(nearest_calls[['contractSymbol','strike','bid','ask','price','Sector','lastPrice']])
    print(index)


