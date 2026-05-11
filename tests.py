import pandas as pd
import unittest

from mcmc import calculate_markov_chain, monte_carlo_sim, calculate_price_move_distribution

class TestCalculatePriceMoveDistribution(unittest.TestCase):
    def test_basic(self):
        '''calculate_price_move_distribition: test a standard input'''

        
        data = pd.DataFrame(data=[10, 10.3, 10.8, 10.6, 10, 11, 12, 12, \
                                  12.5, 12.25, 12.58, 12.18, 17.18, 14.18])

        correct_answers = {'large gain': [5],
                           'small gain': [0.3, 0.5, 1, 1, 0.5, 0.33],
                           'no movement': [0],
                           'small loss': [-0.2, -0.6, -0.25, -0.4],
                           'large loss': [-3]}

        bins, pom = calculate_price_move_distribution(data)

        for b in bins:
            self.assertEqual(bins[b], correct_answers[b])


class TestCalculateMarkovChain(unittest.TestCase):
    def test_basic(self):
        '''calculate_markov_chain: check for expected result from model input'''
        d = pd.DataFrame(data=[10, 10, 11, 12.5, 7.5, 4.5, 8.5, 13.5, 19.5, 14.75])
        expected = [[0, 0, 1, 0, 0],\
                    [0, 2/3, 0, 0, 1/3],\
                    [0, 0, 1/2, 0, 1/2],\
                    [0, 1, 0, 0, 0],\
                    [0, 0, 0, 1, 0]]
        result = calculate_markov_chain(d)
        
        for i in range(len(result)):
            self.assertListEqual(list(result[i]), expected[i])
        return

    def test_always_gain(self):
        '''calculate_markov_chain: edge case when price data always increases (divide by 0)'''
        d = pd.DataFrame(data=[10, 11, 12.5, 17.5, 20.5, 24.5, 29.5, 35.5, 40.25])
        expected = [[0, 0, 0, 0, 0],\
                    [0, 3/4, 1/4, 0, 0],\
                    [0, 2/3, 1/3, 0, 0],\
                    [0, 0, 0, 0, 0],\
                    [0, 0, 0, 0, 0]]
        result = calculate_markov_chain(d)

        for i in range(len(result)):
            self.assertListEqual(list(result[i]), expected[i])            
        return

    def test_always_lose(self):
        '''calculate_markov_chain: edge case when price data always decreases (divide by 0)'''
        d = pd.DataFrame(data=[41, 40, 38.5, 33.5, 30.5, 26.5, 21.5, 15.5, 10.75])
        expected = [[0, 0, 0, 0, 0],\
                    [0, 0, 0, 0, 0],\
                    [0, 0, 0, 0, 0],\
                    [0, 0, 0, 1/3, 2/3],\
                    [0, 0, 0, 1/4, 3/4]]
        result = calculate_markov_chain(d)

        for i in range(len(result)):
            self.assertListEqual(list(result[i]), expected[i])            
        return

    def test_no_movement(self):
        '''calculate_markov_chain: edge case where the data never increases or decreases'''
        d = pd.DataFrame(data=[10, 10, 10, 10, 10, 10])
        expected = [[1, 0, 0, 0, 0],\
                    [0, 0, 0, 0, 0],\
                    [0, 0, 0, 0, 0],\
                    [0, 0, 0, 0, 0],\
                    [0, 0, 0, 0, 0]]
        result = calculate_markov_chain(d)

        for i in range(len(result)):
            self.assertListEqual(list(result[i]), expected[i])
        return

class TestMonteCarloSim(unittest.TestCase):
    def test_always_gain(self):
        '''random_walk: edge case where markov chain has form [[1,0],[0,0]] '''
        depth = 100
        pts = monte_carlo_sim([[1,0], [0,0]], depth, 0)

        # we cannot directly compare python lists, so we compare elementwise instead
        verification = list(map(lambda x: x[0] == x[1], zip(pts, range(1, depth+1))))
        self.assertTrue(all(verification))

    def test_always_loss(self):
        '''random_walk: edge case where markov chain has form [[0,0], [0,1]]'''
        depth = 100
        pts = monte_carlo_sim([[0,0], [0,1]], depth, 1)

        verification = list(map(lambda x: x[0] == x[1], zip(pts, range(-1, -depth-1, -1))))
        self.assertTrue(all(verification))
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
