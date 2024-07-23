import tkinter as tk
from tkinter import ttk, BOTH
import yfinance as yf
import pandas as pd

DEFAULT_INPUT = 'AAPL'


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

def _close_tab(self,notebook, tab_id):
    notebook.forget(tab_id)

# def add_ticker_tab():
def on_entry_click(event):
    """Function to be called when the entry widget is clicked."""
    if ticker_input.get() == DEFAULT_INPUT:
        ticker_input.delete(0, tk.END)  # delete all the text in the entry


def on_focus_out(event):
    """Function to be called when the entry widget loses focus."""
    if ticker_input.get() == "":
        ticker_input.insert(0, DEFAULT_INPUT)


if __name__ == '__main__':
    # potentials=('ROCK','LEN','CCS','GRBK','HZO','NX','HOLI')
    # for tick in potentials:
    #     print(tick,finance_vs_MC(tick))

    app = tk.Tk()
    app.geometry('800x600')

    notebook = ttk.Notebook(app)
    notebook.pack(expand=1, fill=BOTH)
    entry_frame = tk.Frame(notebook,bg='lightblue')
   
    widget_frame=tk.Frame(entry_frame,bg='lightblue')
    ticker_input = tk.Entry(widget_frame)
    ticker_input.insert(0, DEFAULT_INPUT)
    ticker_input.bind("<FocusIn>", on_entry_click)
    ticker_input.bind("<FocusOut>", on_focus_out)
    sub_btn = tk.Button(widget_frame, text='Submit')
    tk.Label(widget_frame, text='Ticker of Interest').pack()
    ticker_input.pack()
    sub_btn.pack()

    widget_frame.place(relx=0.5, rely=0.5, anchor="center")
    notebook.add(entry_frame, text='Entry')
    app.mainloop()
