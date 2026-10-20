# from faicons import icon_svg
# from dash import dcc
from Database.database import DataBase
from Domain.monte_carlo_simulation import MonteCarloSimulation as MCS
from Domain.security import Security
from Domain.strategy import n_day_sma, n_day_ema
from dotenv import load_dotenv
from Errors.errors import InvalidDateFormatException
import os
import pandas as pd
from pathlib import Path
import plotly.express as px
import seaborn as sns
from shiny import reactive, req
from shiny.express import input, module, render, ui
from shinywidgets import render_plotly
import sqlite3

load_dotenv()

app_dir = Path(__file__).parent
ui.page_opts(title="Securities Dashboard", fillable=True)

DB_PATH = os.getenv('AT_DATABASE_PATH')


database = DataBase(DB_PATH)
con = database.open_con()
cur = database.open_cur()
tickers = database.run_query('SELECT SecurityTicker FROM Securities;')
tickers = [ticker[0] for ticker in tickers.fetchall()]

global_current_security = reactive.value(Security('A', database))

def update_global_current_security(security: str):
    new_security = Security(security, database)
    global_current_security.set(new_security)
    return global_current_security

with ui.sidebar(title='Dashboard Controls'):
    ui.input_selectize('ticker', 'Select Ticker',
                       tickers )

    @reactive.effect
    @reactive.event(input.ticker)
    def _():
        req(input.ticker())
        update_global_current_security(input.ticker())
    ui.input_selectize('lower_chart', 'Select a chart to view',
                       ['50/200 SMA', 'EMA', 'RSI', 'Monte Carlo Simulation'])



with ui.layout_columns(col_widths=[12, 12]):

    with ui.card():
        @render_plotly
        def price_chart():
            try:
                hist = global_current_security.get().get_history()
            except InvalidDateFormatException:
                # temporary until I add a proper logger
                print('Invalid date')
                return px.scatter_3d().add_annotation(text=f'Attempted to retrieve security history with an invalid date.  Refer to the logs.', showarrow=False, font={"size":20, 'color': 'red'})

            print(input.ticker())
            print(global_current_security.get())
            return px.line(hist, x=hist.index, y='Close', title=f'Closing Prices for {global_current_security.get().ticker}')
            
    with ui.card():
        @render_plotly
        def dynamic_chart():
            req(input.lower_chart())
            if input.lower_chart() == 'Monte Carlo Simulation':
                try:
                    hist = global_current_security.get().get_history()
                except InvalidDateFormatException:
                    # temporary until logger
                    print('Invalid date')
                    return px.scatter_3d().add_annotation(text=f'Attempted to retrieve security history with an invalid date.  Refer to the logs.', showarrow=False, font={"size":20, 'color': 'red'})

                mcs = MCS(hist)
                pts = mcs.monte_carlo_sim(500)
                return px.line(pts)
            elif input.lower_chart() == '50/200 SMA':
                sma_50 = n_day_sma(global_current_security.get(), 450, 50)
                sma_50 = sma_50[~sma_50.isna()]
                sma_50.rename('50 Day SMA', inplace=True)

                sma_200 = n_day_sma(global_current_security.get(), 450, 200)
                sma_200 = sma_200[~sma_200.isna()]
                sma_200.rename('200 Day SMA', inplace=True)

                most_recent_50 = sma_50.tail(n=1).values[0]
                most_recent_200 = sma_200.tail(n=1).values[0]
                ratio = most_recent_50 / most_recent_200
                if ratio < 1:
                    print('SELL')
                else:
                    print('HOLD')
                print(ratio)
                

                combined = pd.concat([sma_50, sma_200], axis=1)
                return px.line(combined, title=f'50/200 Day SMA',labels={'Datetime': 'Date', 'value': 'SMA'})

            elif input.lower_chart() == 'EMA':
                ema_50 = n_day_ema(global_current_security.get(), 50)
                return px.line(ema_50, title=f'50 Day EMA', labels={'Datetime': 'Date'})



ui.include_css(app_dir / "styles.css")

con.close()
