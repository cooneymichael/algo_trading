################################################################################
#
# File:    test_monte_carlo_simulation.py
# Author:  Michael Cooney
# Purpose: Unit tests for the markov chain and monte carlo simulation.
#
################################################################################

import pandas as pd
import unittest
from unittest.mock import Mock, MagicMock, patch

# import monte_carlo_simulation
# from monte_carlo_simulation import calculate_markov_chain, monte_carlo_sim, calculate_price_move_distribution
from monte_carlo_simulation import MonteCarloSimulation as MCS


class TestCalculatePriceMoveDistribution(unittest.TestCase):
    def test_basic(self):
        '''calculate_price_move_distribition: test a standard input'''

        
        data = pd.DataFrame(data=[10, 10.3, 10.8, 10.6, 10, 11, 12, 12, \
                                  12.5, 12.25, 12.58, 12.18, 17.18, 14.18])

        mcs = MCS(data)

        correct_answers = {'large gain': [5],
                           'small gain': [0.3, 0.5, 1, 1, 0.5, 0.33],
                           'no movement': [0],
                           'small loss': [-0.2, -0.6, -0.25, -0.4],
                           'large loss': [-3]}

        bins = mcs._calculate_price_move_distribution()

        for b in bins:
            self.assertEqual(bins[b], correct_answers[b])


class TestCalculateMarkovChain(unittest.TestCase):
    def test_basic(self):
        '''calculate_markov_chain: check for expected result from model input'''
        d = pd.DataFrame(data=[10, 10, 11, 12.5, 7.5, 4.5, 8.5, 13.5, 19.5, 14.75])
        mcs = MCS(d)

        expected = [[0, 0, 1, 0, 0],\
                    [0, 2/3, 0, 0, 1/3],\
                    [0, 0, 1/2, 0, 1/2],\
                    [0, 1, 0, 0, 0],\
                    [0, 0, 0, 1, 0]]
        result = mcs._calculate_markov_chain()
        
        for i in range(len(result)):
            self.assertListEqual(list(result[i]), expected[i])
        return


    def test_always_gain(self):
        '''calculate_markov_chain: edge case when price data always increases (divide by 0)'''
        d = pd.DataFrame(data=[10, 11, 12.5, 17.5, 20.5, 24.5, 29.5, 35.5, 40.25])
        mcs = MCS(d)
        expected = [[0, 0, 0, 0, 0],\
                    [0, 3/4, 1/4, 0, 0],\
                    [0, 2/3, 1/3, 0, 0],\
                    [0, 0, 0, 0, 0],\
                    [0, 0, 0, 0, 0]]
        result = mcs._calculate_markov_chain()

        for i in range(len(result)):
            self.assertListEqual(list(result[i]), expected[i])            
        return


    def test_always_lose(self):
        '''calculate_markov_chain: edge case when price data always decreases (divide by 0)'''
        d = pd.DataFrame(data=[41, 40, 38.5, 33.5, 30.5, 26.5, 21.5, 15.5, 10.75])
        mcs = MCS(d)
        expected = [[0, 0, 0, 0, 0],\
                    [0, 0, 0, 0, 0],\
                    [0, 0, 0, 0, 0],\
                    [0, 0, 0, 1/3, 2/3],\
                    [0, 0, 0, 1/4, 3/4]]
        result = mcs._calculate_markov_chain()

        for i in range(len(result)):
            self.assertListEqual(list(result[i]), expected[i])            
        return


    def test_no_movement(self):
        '''calculate_markov_chain: edge case where the data never increases or decreases'''
        d = pd.DataFrame(data=[10, 10, 10, 10, 10, 10])
        mcs = MCS(d)
        expected = [[1, 0, 0, 0, 0],\
                    [0, 0, 0, 0, 0],\
                    [0, 0, 0, 0, 0],\
                    [0, 0, 0, 0, 0],\
                    [0, 0, 0, 0, 0]]
        result = mcs._calculate_markov_chain()

        for i in range(len(result)):
            self.assertListEqual(list(result[i]), expected[i])
        return

class TestMonteCarloSim(unittest.TestCase):
    def test_always_gain(self):
        '''monte_carlo_sim: edge case where markov chain always chooses a large gain state'''

        # always a large gain
        markov_chain = [[0,0,0,0,0],\
                        [0,1,0,0,0],\
                        [0,0,0,0,0],\
                        [0,0,0,0,0],\
                        [0,0,0,0,0]]

        movement_distribution = {
            'no movement': [-1],
            'large gain': [1],
            'small gain': [-1],
            'small loss': [-1],
            'large loss': [-1],
        }

        cls = MagicMock()
        cls._calculate_markov_chain = Mock(return_value=markov_chain)
        cls._calculate_price_move_distribution = Mock(return_value=movement_distribution)

        depth = 100

        with patch('monte_carlo_simulation.MonteCarloSimulation', return_value=cls, autospec=True) as mock_mcs:
            pts = mock_mcs.monte_carlo_sim(depth)
            verification = list(map(lambda x: x[0] == x[1], zip(pts, range(1, depth+1))))
            self.assertTrue(all(verification))


    def test_always_loss(self):
        '''monte_carlo_sim: edge case where markov chain always chooses a large loss state'''
        # always a large loss
        markov_chain = [[0,0,0,0,0],\
                        [0,0,0,0,0],\
                        [0,0,0,0,0],\
                        [0,0,0,0,0],\
                        [0,0,0,0,1]]

        movement_distribution = {
            'no movement': [1],
            'large gain': [1],
            'small gain': [1],
            'small loss': [1],
            'large loss': [-1],
        }

        cls = MagicMock()
        cls._calculate_markov_chain = Mock(return_value=markov_chain)
        cls._calculate_price_move_distribution = Mock(return_value=movement_distribution)
        
        depth = 100

        with patch('monte_carlo_simulation.MonteCarloSimulation', return_value=cls, autospec=True) as mock_mcs:
            pts = mock_mcs.monte_carlo_sim(depth)
            verification = list(map(lambda x: x[0] == x[1], zip(pts, range(-1, -depth-1, -1))))
            self.assertTrue(all(verification))
        
if __name__ == '__main__':
    unittest.main(verbosity=1)

