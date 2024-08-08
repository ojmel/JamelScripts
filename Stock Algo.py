import sys
import pyqtgraph as pg
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, \
    QSizePolicy
import yfinance as yf
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib
from datetime import datetime, timedelta
#TODO exception handling for wrong tickers
#TODO making text expand with window size

#live_price = stock.history(period='1d', interval='1m')
DEFAULT_INPUT = 'AAPL'
SPY_MODEL = r'C:\Users\jamel\PycharmProjects\JamelScripts\spy_predictor.pkl'
# Profitable?, bargraph income, revenue, debt to asset, scores and market cap

def finance_vs_MC(ticker: str):
    ticker = yf.Ticker(ticker)
    financials=ticker.financials
    balance=ticker.balance_sheet
    if not financials:
        return
    revenue = financials.loc['Total Revenue'][0]
    income = financials.loc['Net Income'][0]
    assets = balance.loc['Total Assets'][0]
    liabilities = balance.loc['Total Liabilities Net Minority Interest'][0]
    market_cap = ticker.fast_info['marketCap']
    # formula
    # AnnualRevenue+(Assets-Liabilities)
    revenue_value = revenue + (assets - liabilities)
    # formula
    # AnnualIncome+(Assets-Liabilities)
    income_value = income + (assets - liabilities)
    return revenue_value / market_cap, income_value / market_cap


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
        self.button = QPushButton('Submit')
        self.line_edit=QLineEdit()
        self.setWindowTitle(window_title)
        self.setGeometry(0, 0, *shape)
        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)
        self.create_submission_tab()
        self.show()

    def create_tab(self,layout,title:str='poop'):
        tab = QWidget()
        tab.setLayout(layout)
        tab.setStyleSheet("""
            QWidget {
                background-color: #87CEEB;  /* Light sky blue */
            }
        """)

        self.addTab(tab, title)

    def create_submission_tab(self):
        tab_layout = QVBoxLayout()
        tab_layout.setAlignment(Qt.AlignCenter)
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)


        label=QLabel('Ticker of Interest')
        label.adjustSize()
        tab_layout.addWidget(label, alignment=Qt.AlignHCenter)

        self.line_edit.textChanged.connect(self.to_upper)
        self.line_edit.setPlaceholderText('Enter Ticker')
        self.line_edit.setStyleSheet("""
                    QLineEdit {
                        background-color: #FFFFFF;  /* White background for full opacity */
                        border: 1px solid #CCCCCC;  /* Light gray border */
                        padding: 5px;               /* Padding inside the line edit */
                    }
                """)
        tab_layout.addWidget(self.line_edit, alignment=Qt.AlignHCenter)

        self.button.clicked.connect(self.create_ticker_tab)
        self.line_edit.returnPressed.connect(self.create_ticker_tab)
        tab_layout.addWidget(self.button, alignment=Qt.AlignHCenter)

        self.create_tab(tab_layout)

    def close_tab(self, index):
        self.removeTab(index)

    def create_ticker_tab(self):
        if self.line_edit.text():
            tab_layout = QVBoxLayout()
            tab_layout.setAlignment(Qt.AlignCenter)
            tab_layout.setContentsMargins(0, 0, 0, 0)
            tab_layout.setSpacing(0)
            try:
                rev,inc=finance_vs_MC(self.line_edit.text())
                plot_graph = pg.PlotWidget()
                plot_graph.plot([rev],[inc])
                label = QLabel(f'{rev}:{inc}')
                label.adjustSize()
                tab_layout.addWidget(label, alignment=Qt.AlignHCenter)
                self.create_tab(tab_layout,self.line_edit.text() )
                self.line_edit.clear()
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print('error')

    def to_upper(self, text):
        self.line_edit.blockSignals(True)
        self.line_edit.setText(text.upper())
        self.line_edit.blockSignals(False)

def run_app():
    app = QApplication(sys.argv)
    main_window=TabbedWindow('TickerSifter')
    sys.exit(app.exec_())

if __name__ == '__main__':
    # run_app()
    print(yf.Ticker('SPY').financials)
    # potentials=('ROCK','LEN','CCS','GRBK','HZO','NX','HOLI')
    # for tick in potentials:
    #     print(tick,finance_vs_MC(tick))
    # maybe i should go for up or down movement in classifieer
    # print(spy_prices[spy_prices['PercentChange']<-0.015])
    # print(spy_prices.loc[133,'PercentChange'])
    # print(predict_spy_movement())


