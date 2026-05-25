################################################################################
#
# File:    monte_carlo_simulation.py
# Author:  Michael Cooney
# Purpose: Define the implementation of a markov chain and monte carlo
#          simulation to predict the future of a security's price movement.
#          Currently, code is written as functions, but will soon be refactored
#          as a class.
#
################################################################################


import datetime as dt
import holidays
from errors import NoNewDataError
import numpy as np
import pandas as pd
import sqlite3
import yfinance as yf


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
    # print(price_movements_pos)
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
        

def calculate_price_move_distribution(data: pd.DataFrame) -> dict[str: list[float]]:
    '''Calculate the distribution of price movements for the input security.'''


    price_movements = get_price_movements(data)
    # categorize price movements by standard deviation
    bins = {
        'no movement': [],
        'large gain': [],
        'small gain': [],
        'small loss': [],
        'large loss': [],
    }

    stddev = get_standard_deviation_of_movement(price_movements)

    for movement in price_movements:
        current_state = get_state(movement, stddev)
        bins[current_state].append(movement)
    
    return bins


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
    # print(stddev)
    # print(2 * stddev)
    prev_state = get_state(price_movements[0], stddev)

    for i in range(1, len(price_movements)):
        current_state = get_state(price_movements[i], stddev)
        coord1 = get_coordinates_from_state(prev_state)
        coord2 = get_coordinates_from_state(current_state)
        markov_chain[coord1, coord2] += 1
        counters[coord1] += 1
        prev_state = current_state

    # print(counters)
    for i in range(len(markov_chain)):
        if counters[i] == 0:
            continue
        markov_chain[i] = list(map(lambda x: x/counters[i], markov_chain[i]))
    
    return markov_chain


def monte_carlo_sim(markov_chain: list[list[float]],\
                    movements_distribution: dict[str: list[float]],\
                    last_price: float,\
                    depth: int,\
                    initial_state: int) -> list[float]:
    '''Average a list of points over thousands of random walks.  Points should
    be real numbers. Return the averaged list to be visualized or analyzed.

    key word arguments:
    markov_chain --  a 5x5 matrix holding probabilities for gains and losses
    depth --         the number of future events to simulate
    initial_state -- a pointer to a row in markov_chain. 0 represents a gain, 1 represents a loss
    '''

    # points = []
    simulations = np.zeros((1000, depth))

    for idx, _ in enumerate(simulations):
        state_pointer = initial_state
        # counter = 0
        simulated_price = last_price

        for i in range(depth):
            new_state = np.random.choice([0, 1, 2, 3, 4], p=markov_chain[state_pointer])
            if state_pointer != new_state:
                state_pointer = new_state

            relevant_price_move_dist = list(movements_distribution.values())[new_state]
            price_change = np.random.choice(relevant_price_move_dist)
            simulated_price += price_change

            simulations[idx][i] = simulated_price

    simulation = np.average(simulations, axis=0)
    return simulation
