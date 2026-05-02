import numpy as np
import pandas as pd
import sqlite3
import sys

################################################################################
#
# File:   mcmc.py
# Author: Michael Cooney
# Goal:   Create a simple two-step simulation of future stock conditions using
#         a markov chain trained on past stock data
#
#         In the future, this is be put into a class or module  with other
#         simulation and analysis functions.
################################################################################

# functions:
#  get_security_history
#  calculate_markov_chain
#  random_walk

DB_PATH = '../Data/Data/stocks.db'

def get_security_history(ticker: str, start: int=None) -> pd.DataFrame:
    '''Get the closing price history of a ticker, either for all time or beginning
    from start up to the most recent data.  If start is more specific than a year
    then it should be in the format yyyy-mm-dd.  Data is return in a pandas dataframe'''
    con = sqlite3.connect(DB_PATH)

    query = f'SELECT Datetime, Close FROM History WHERE SecurityId =\
    (SELECT SecurityId FROM Securities WHERE SecurityTicker = \'{ticker}\')'

    if start is not None:
        query += f' AND Datetime > {str(start)}'
    query += ';'

    data = pd.read_sql(query, con, index_col='Datetime')
    con.close()
    
    return data


def calculate_markov_chain(data: pd.DataFrame) -> list[list[float]]:
    # markov chain as matrix
    chain = [[0, 0],[0, 0]]
    gain_counter = 0
    loss_counter = 0

    def update_chain():
        nonlocal chain
        nonlocal gain_counter
        nonlocal loss_counter

        if prev_state:
            gain_counter += 1
        else:
            loss_counter += 1

        chain[abs(prev_state-1)][abs(current_state-1)] += 1

    def update_previous_values():
        nonlocal prev_state
        nonlocal prev_price
        prev_state = current_state
        prev_price = it.value

    # iterate over the prices, tracking gains and losses
    # closing_prices = data.values.flatten()
    closing_prices = np.array([1,2,3,2,3,1])
    it = np.nditer(closing_prices)
    prev_price = it.value
    it.iternext()
    prev_state = 1 if it.value - prev_price >= 0 else 0
    prev_price = it.value
    it.iternext()
    current_state = 1 if it.value - prev_price >= 0 else 0

    update_chain()
    update_previous_values()
    while it.iternext():
        current_state = 1 if it.value - prev_price >= 0 else 0
        update_chain()
        update_previous_values()
        
    # transform counters into probabilites for markov chain
    chain[0] = list(map(lambda x: x / (gain_counter if gain_counter > 0 else 1), chain[0]))
    chain[1] = list(map(lambda x: x / (loss_counter if loss_counter > 0 else 1), chain[1]))
    return chain


def random_walk(markov_chain: list[list[float]]) -> list[float]:
    '''Average a list of points over thousands of random walks.  Points should
    be real numbers. Return the averaged list to be visualized or analyzed.'''
    return

if __name__ == '__main__':
    # ewy_history = get_security_history('EWY', 2012)
    # print(ewy_history)

    mc = calculate_markov_chain('a')
    print(mc)
