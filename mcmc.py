import matplotlib.pyplot as plt
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


def calculate_price_move_distribution(data: pd.DataFrame) -> dict[str: list[float]] and np.array:
    '''Calculate the distribution of price movements for the input security.'''

    price_movements = np.zeros(shape=data.shape[0]-1)
    closing_prices = data.values.flatten()
    for i in range(1, len(closing_prices)):
        price_movements[i-1] = np.around(closing_prices[i] - closing_prices[i-1], 2)

    # categorize price movements by standard deviation
    bins = {
        'large gain': [],
        'small gain': [],
        'no movement': [],
        'small loss': [],
        'large loss': [],
    }

    # we only care about the magnitude of price movement, not cardinality
    price_movements_pos = list(map(lambda x: abs(x), price_movements))
    stddev = np.std(price_movements_pos)
    del price_movements_pos

    for i in price_movements:
        if i == 0:
            bins['no movement'].append(i)
        elif abs(i) >= stddev*2:
            if i > 0:
                bins['large gain'].append(i)
            else:
                bins['large loss'].append(i)
        else:
            if i > 0:
                bins['small gain'].append(i)
            else:
                bins['small loss'].append(i)

    # calculate probability of each category being sampled
    probability_of_movements = np.zeros(shape=5)
    for i, k in enumerate(bins.keys()):
        probability_of_movements[i] = len(bins[k]) / len(price_movements)

    return bins, probability_of_movements


def calculate_markov_chain(data: pd.DataFrame) -> list[list[float]]:
    '''Calculate a markov chain probability matrix/state diagram using the data parameter.
    The result will have the form:
    -------------
    |g->g |g->l |
    |     |     |
    |-----|-----|
    |l->g |l->l |
    |     |     |
    -------------
    Where g is a gain and l is a loss
    '''
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
    closing_prices = data.values.flatten()
    # closing_prices = np.array([1,2,3,2,3,1])
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


def random_walk(markov_chain: list[list[float]], depth: int, initial_state: int) -> list[float]:
    '''Average a list of points over thousands of random walks.  Points should
    be real numbers. Return the averaged list to be visualized or analyzed.

    key word arguments:
    markov_chain --  a 2x2 matrix holding probabilities for gains and losses
    depth --         the number of future events to simulate
    initial_state -- a pointer to a row in markov_chain. 0 represents a gain, 1 represents a loss
    '''

    # points = []
    simulations = np.zeros((1000, depth))

    for idx, _ in enumerate(simulations):
        state_pointer = initial_state
        counter = 0

        for i in range(depth):
            new_state = np.random.choice([0,1], p=markov_chain[state_pointer])
            if state_pointer != new_state:
                state_pointer = new_state

            # logic is inverted (gain = 0) because matrix is 0-indexed
            if not new_state:
                counter += 1
            else:
                counter -= 1

            simulations[idx][i] = counter

    simulation = np.average(simulations, axis=0)
    return simulation

if __name__ == '__main__':
    # ewy_history = get_security_history('EWY', 2012)
    # print(ewy_history)

    # d = pd.DataFrame(data=[1, 1.5, 5, 3, 4, 5, 6, 4.75])
    # dist, pom = calculate_price_move_distribution(d)

    # mc = calculate_markov_chain('a')
    # print(mc)

    # pts = random_walk([[2/3,1/3],[3/4, 1/4]], 1000, 0)
    # # pts = random_walk([[1,0],[1, 0]], 1000, 0)
    # pts = pd.Series(pts)
    # print(pts)
    # pts.plot()
    # plt.show()

