# from faicons import icon_svg
from monte_carlo_simulation import MonteCarloSimulation as MCS
import pandas as pd
from pathlib import Path
import plotly.express as px
import seaborn as sns
from security import Security
from shiny import reactive, req
from shiny.express import input, module, render, ui
from shinywidgets import render_plotly
import sqlite3

app_dir = Path(__file__).parent
ui.page_opts(title="Securities Dashboard", fillable=True)

DB_PATH = Path('./../../../Data/Data/stocks.db')

con = sqlite3.connect(DB_PATH)
cur = con.cursor()
tickers = cur.execute('SELECT SecurityTicker FROM Securities;')
tickers = tickers.fetchall()
tickers = [ticker[0] for ticker in tickers]

global_current_security = reactive.value(Security('A', db_path=DB_PATH))

def update_global_current_security(security: str):
    new_security = Security(security, db_path=DB_PATH)
    global_current_security.set(new_security)
    return global_current_security
    # global_current_security.set(Security(security, db_path=DB_PATH))

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
            hist = global_current_security.get().get_history()
            print(input.ticker())
            print(global_current_security.get())
            return px.line(hist, x=hist.index, y='Close', title=f'Closing Prices for {global_current_security.get().ticker}')
            
    with ui.card():
        @render_plotly
        def dynamic_chart():
            req(input.lower_chart())
            if input.lower_chart() == 'Monte Carlo Simulation':
                hist = global_current_security.get().get_history()
                mcs = MCS(hist)
                pts = mcs.monte_carlo_sim(500)
                return px.line(pts)



ui.include_css(app_dir / "styles.css")

con.close()
