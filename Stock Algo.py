from yahoofinancials import YahooFinancials as yl
import yfinance as yf
import pandas as pd
def finance_vs_MC(ticker:str):

    ticker=yf.Ticker(ticker)
    revenue=ticker.financials.loc['Total Revenue'][0]
    income=ticker.financials.loc['Net Income'][0]
    assets=ticker.balance_sheet.loc['Total Assets'][0]
    liabilities=ticker.balance_sheet.loc['Total Liabilities Net Minority Interest'][0]
    market_cap=ticker.fast_info['marketCap']
    # formula
    # AnnualRevenue+(Assets-Liabilities)
    revenue_value=revenue+(assets-liabilities)
    # formula
    # AnnualIncome+(Assets-Liabilities)
    income_value = income + (assets - liabilities)
    return revenue_value/market_cap,income_value/market_cap
if __name__=='__main__':
    potentials=('ROCK','LEN','CCS','GRBK','HZO','NX','HOLI')
    for tick in potentials:
        print(tick,finance_vs_MC(tick))