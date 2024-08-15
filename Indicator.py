import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
from json import load
LI=r'C:\Users\jamel\PycharmProjects\JamelScripts\smtp.json'
with open(LI, 'rb') as jfile:
    logon_dict: dict = load(jfile)
def send_email(msg:str):
    #SERVER = "localhost"

    FROM = logon_dict['email']

    # TO = [f"{logon_dict['number']}@txt.att.net"] # must be a list
    TO=logon_dict['email']
    SUBJECT = "HI Volume"

    MSG=f'Subject: {SUBJECT}\n\n{msg}'

    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(FROM, logon_dict['password'])
    server.sendmail(FROM, TO, MSG)
    server.quit()

frequency=1
live_price = yf.Ticker('SPY').history(period='1d', interval=f'{frequency}m')
volume_info=live_price['Volume'].iloc[-15:-1]
if volume_info.max()>300_000:
    send_email(f'SPY Volume at {volume_info.max()} at {str(volume_info.idxmax())}')

# live_price=live_price.reset_index(drop=True)
# live_price['dy_dx']=live_price['High'].diff()/frequency
