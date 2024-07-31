import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, \
    QSizePolicy
import yfinance as yf
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib
from datetime import datetime, timedelta

#live_price = stock.history(period='1d', interval='1m')
DEFAULT_INPUT = 'AAPL'
SPY_MODEL = r'C:\Users\jamel\PycharmProjects\JamelScripts\spy_predictor.pkl'


def finance_vs_MC(ticker: str):
    ticker = yf.Ticker(ticker)
    revenue = ticker.financials.loc['Total Revenue'][0]
    income = ticker.financials.loc['Net Income'][0]
    assets = ticker.balance_sheet.loc['Total Assets'][0]
    liabilities = ticker.balance_sheet.loc['Total Liabilities Net Minority Interest'][0]
    market_cap = ticker.fast_info['marketCap']
    # formula
    # AnnualRevenue+(Assets-Liabilities)
    revenue_value = revenue + (assets - liabilities)
    # formula
    # AnnualIncome+(Assets-Liabilities)
    income_value = income + (assets - liabilities)
    return revenue_value / market_cap, income_value / market_cap


def _close_tab(self, notebook, tab_id):
    notebook.forget(tab_id)


def load_lr_model():
    return joblib.load(SPY_MODEL)


def get_lagged_data(change=10, today=True):
    start = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d") if today else datetime.now().strftime("%Y-%m-%d")
    lag_day = (datetime.now() - timedelta(days=1 + change)).strftime("%Y-%m-%d")
    lagged_data = yf.download('SPY', start=lag_day, end=start)
    return lagged_data


def predict_spy_movement(today=True):
    spy_model: LinearRegression = load_lr_model()
    lag_input = single_day_lag(today)
    return spy_model.predict(lag_input) * 100


def single_day_lag(today=True):
    lagged_data = get_lagged_data(20, today)
    lagged_data["Percent Change Lag 1"] = lagged_data['Adj Close'].pct_change()
    lagged_data = lagged_data.reset_index()
    lagged_data = lagged_data.drop(columns=['Open', 'High', 'Low', 'Close', 'Adj Close', 'Date', 'Volume'])
    for i in range(2, 6):
        lagged_data[f'Percent Change Lag {i}'] = lagged_data['Percent Change Lag 1'].shift(i)
    lagged_data = lagged_data.dropna()
    single_lag = lagged_data.iloc[-1:, :]
    return single_lag


def get_previous_moves():
    start = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    lag_day = (datetime.now() - timedelta(days=356)).strftime("%Y-%m-%d")
    year_data = yf.download('SPY', start=lag_day, end=start)
    year_data["Percent Change"] = year_data['Adj Close'].pct_change()
    year_data = year_data.drop(columns=['Open', 'High', 'Low', 'Close', 'Adj Close', 'Date', 'Volume'])
    print(year_data[year_data['PercentChange'] < -0.015])
    print(year_data.loc[133, 'PercentChange'])


class TabbedWindow(QTabWidget):
    def __init__(self, window_title:str, shape: tuple[int] = (800, 800)):
        super().__init__()
        self.button = None
        self.line_edit = None
        self.setWindowTitle(window_title)
        self.setGeometry(0, 0, *shape)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        # self.setCentralWidget(self.tab_widget)
    def create_tab(self,layout,title:str='poop',):
        tab = QWidget()
        tab.setLayout(layout)
        self.addTab(tab, title)
        # widget.returnPressed.connect(self.return_pressed)
    def create_submission_tab(self):
        tab_layout = QVBoxLayout()
        label=QLabel('Ticker of Interest')
        label.setFixedSize(200,200)
        # label.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        # label.setAlignment(Qt.AlignHCenter)

        tab_layout.addWidget(label)
        label.adjustSize()
        self.line_edit=QLineEdit()
        self.line_edit.setPlaceholderText('Enter Ticker')
        tab_layout.addWidget(self.line_edit)
        self.button = QPushButton('Submit')
        tab_layout.addWidget(self.button)
        self.create_tab(tab_layout)
    def close_tab(self, index):
        self.removeTab(index)


if __name__ == '__main__':
    # potentials=('ROCK','LEN','CCS','GRBK','HZO','NX','HOLI')
    # for tick in potentials:
    #     print(tick,finance_vs_MC(tick))
    # maybe i should go for up or down movement in classifieer
    # print(spy_prices[spy_prices['PercentChange']<-0.015])
    # print(spy_prices.loc[133,'PercentChange'])
    # print(predict_spy_movement())

    app = QApplication(sys.argv)
    main_window = TabbedWindow('TickerSifter')
    main_window.create_submission_tab()
    main_window.show()
    sys.exit(app.exec_())

