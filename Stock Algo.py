from yahoofinancials import YahooFinancials as yl
import yfinance as yf
import pandas as pd
SoI=open('StocksofInterest','r').readlines()
# print(SoI[0]+SoI[1])
# print(yl(SoI[0:2]).get_stock_earnings_data())
# print(yf.Ticker('SMTC').earnings_dates['EPS Estimate'])
# SoI=[yf.Ticker(x) for x in SoI[0:2]]
# print(type(yf.Ticker('STRR').calendar))
yf.Ticker('STRR').calendar.to_csv('STRRearnings.csv')