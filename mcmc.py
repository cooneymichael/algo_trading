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


def get_state(movement: float, stddev: float) -> str:
    '''Convert a price movement into a categorical state.'''
    if movement == 0.00:
        return 'no movement'
    elif abs(movement) >= 2*stddev:
        if movement > 0:
            return 'large gain'
        else:
            return 'large loss'
    else:
        if movement > 0:
            return 'small gain'
        else:
            return 'small loss'


def get_price_movements(prices: pd.DataFrame) -> np.array:
    '''Calculate the movement between each price for a history.'''
    price_movements = np.zeros(shape=prices.shape[0]-1)
    closing_prices = prices.values.flatten()
    for i in range(1, len(closing_prices)):
        price_movements[i-1] = np.around(closing_prices[i] - closing_prices[i-1], 2)
    return price_movements


def get_standard_deviation_of_movement(price_movements: np.array) -> list[float]:
    '''Calculate the standard deviation of a list of price movements.  The
    absolute value of prices is used because we want the deviation of the
    magnitude of movements.

    E.g., a price history of 10.00, 10.05, 10.10, 10.13, 10.10, 10.00
    would have movements of 0.05, 0.05, 0.03, -0.03, -0.10.  The negative
    values add extra distance between the measurements that is not reflected
    in reality.'''

    price_movements_pos = list(map(lambda x: abs(x), price_movements))
    print(price_movements_pos)
    return np.std(price_movements_pos)


def get_coordinates_from_state(state:str) -> int:
    '''Convert a categorical state into a matrix coordinate'''
    match state:
        case 'no movement':
            return 0
        case 'large gain':
            return 1
        case 'small gain':
            return 2
        case 'small loss':
            return 3
        case 'large loss':
            return 4
        case _:
            raise ValueError('This is not a valid state for a Markov Chain')
        


def calculate_markov_chain(data: pd.DataFrame) -> np.ndarray:
    '''Calculate a markov chain probability matrix/state diagram using the data parameter.
    The result will have the form:
    -------------------
    |0->0 |0->1 |...
    |     |     |
    |-----|-----|-----|
    |1->0 |1->l | ...
    |     |     |
    ------------|-----|
    |  :  |  :  |
    |  .  |  .  |


    Where g is a gain and l is a loss
    '''

    # markov chain as matrix
    markov_chain = np.zeros([5,5])
    counters = [0 for _ in range(5)]

    # we are interested in transitions for this function
    price_movements = get_price_movements(data)
    stddev = get_standard_deviation_of_movement(price_movements)
    print(stddev)
    print(2 * stddev)
    prev_state = get_state(price_movements[0], stddev)

    for i in range(1, len(price_movements)):
        current_state = get_state(price_movements[i], stddev)
        coord1 = get_coordinates_from_state(prev_state)
        coord2 = get_coordinates_from_state(current_state)
        markov_chain[coord1, coord2] += 1
        counters[coord1] += 1
        prev_state = current_state

    print(counters)
    for i in range(len(markov_chain)):
        if counters[i] == 0:
            continue
        markov_chain[i] = list(map(lambda x: x/counters[i], markov_chain[i]))
    
    return markov_chain


def monte_carlo_sim(markov_chain: list[list[float]], depth: int, initial_state: int) -> list[float]:
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

    # d = pd.DataFrame(data=[10, 10, 11, 11.5, 6.5, 3.5, 7.5, 12.5, 18.5, 13.75])
    d = pd.DataFrame(data=[10, 10, 11, 12.5, 7.5, 4.5, 8.5, 13.5, 19.5, 14.75])
    dist, pom = calculate_price_move_distribution(d)

    for i in dist:
        print(i, dist[i])
    print()

    print('================================================================================')

    mc = calculate_markov_chain(d)
    print(mc)

    # pts = random_walk([[2/3,1/3],[3/4, 1/4]], 1000, 0)
    # # pts = random_walk([[1,0],[1, 0]], 1000, 0)
    # pts = pd.Series(pts)
    # print(pts)
    # pts.plot()
    # plt.show()

