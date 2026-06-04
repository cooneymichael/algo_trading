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



class MonteCarloSimulation():
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.price_movements = None
    
    def _get_state(self, movement: float, stddev: float) -> str:
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


    # def _get_price_movements(self, prices: pd.DataFrame) -> np.array:
    def _get_price_movements(self) -> np.array:
        '''Calculate the movement between each price for a history.'''
        # price_movements = np.zeros(shape=prices.shape[0]-1)
        price_movements = np.zeros(shape=self.data.shape[0]-1)
        # closing_prices = prices.values.flatten()
        closing_prices = self.data.values.flatten()
        for i in range(1, len(closing_prices)):
            price_movements[i-1] = np.around(closing_prices[i] - closing_prices[i-1], 2)
        return price_movements


    # def _get_standard_deviation_of_movement(self, price_movements: np.array) -> list[float]:
    def _get_standard_deviation_of_movement(self) -> list[float]:
        '''Calculate the standard deviation of a list of price movements.  The
        absolute value of prices is used because we want the deviation of the
        magnitude of movements.
        
        E.g., a price history of 10.00, 10.05, 10.10, 10.13, 10.10, 10.00
        would have movements of 0.05, 0.05, 0.03, -0.03, -0.10.  The negative
        values add extra distance between the measurements that is not reflected
        in reality.'''

        # if self.price_movements is None:
        #     self.price_movements = self._get_price_movements()

        price_movements_pos = list(map(lambda x: abs(x), self.price_movements))
        return np.std(price_movements_pos)


    def _get_coordinates_from_state(self, state:str) -> int:
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
                raise ValueError(f'\'{state}\' is not a valid state for a Markov Chain')
        return
        

    # def _calculate_price_move_distribution(self, data: pd.DataFrame) -> dict[str: list[float]]:
    def _calculate_price_move_distribution(self) -> dict[str: list[float]]:
        '''Calculate the distribution of price movements for the input security.'''
 
        # price_movements = self._get_price_movements()
        if self.price_movements is None:
            self.price_movements = self._get_price_movements()

        # categorize price movements by standard deviation
        bins = {
            'no movement': [],
            'large gain': [],
            'small gain': [],
            'small loss': [],
            'large loss': [],
        }
        
        # stddev = self._get_standard_deviation_of_movement(price_movements)
        stddev = self._get_standard_deviation_of_movement()
        
        for movement in self.price_movements:
        # for movement in self.price_movements:
            current_state = self._get_state(movement, stddev)
            bins[current_state].append(movement)
            
        return bins


    # def _calculate_markov_chain(self, data: pd.DataFrame) -> np.ndarray:
    def _calculate_markov_chain(self) -> np.ndarray:
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
        if self.price_movements is None:
            self.price_movements = self._get_price_movements()
        # price_movements = self._get_price_movements()
        # stddev = self._get_standard_deviation_of_movement(price_movements)
        stddev = self._get_standard_deviation_of_movement()
        prev_state = self._get_state(self.price_movements[0], stddev)
        
        for i in range(1, len(self.price_movements)):
            current_state = self._get_state(self.price_movements[i], stddev)
            coord1 = self._get_coordinates_from_state(prev_state)
            coord2 = self._get_coordinates_from_state(current_state)
            markov_chain[coord1, coord2] += 1
            counters[coord1] += 1
            prev_state = current_state
            
        for i in range(len(markov_chain)):
            if counters[i] == 0:
                continue
            markov_chain[i] = list(map(lambda x: x/counters[i], markov_chain[i]))
            
        return markov_chain


    def monte_carlo_sim(self, depth: int) -> list[float]:
        '''Average a list of points over thousands of random walks.  Points should
        be real numbers. Return the averaged list to be visualized or analyzed.
        
        depth --                  the number of future events to simulate
        '''

        markov_chain = self._calculate_markov_chain()
        movements_distribution = self._calculate_price_move_distribution()

        simulations = np.zeros((1000, depth))

        # choose the most likely state as the initial state
        initial_state = np.argmax(markov_chain.sum(axis=0))
        
        for idx, _ in enumerate(simulations):
            state_pointer = initial_state
            simulated_price = float(np.around(self.data.iloc[self.data.shape[0]-1:]['Close'], 2).values[0])
            
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
