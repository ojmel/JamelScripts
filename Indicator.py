import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

frequency=5
live_price = yf.Ticker('IWM').history(period='1d', interval=f'{frequency}m')
live_price=live_price.reset_index(drop=True)
live_price['dy_dx']=live_price['High'].diff()/frequency
