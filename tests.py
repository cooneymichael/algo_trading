import pandas as pd
import unittest

from mcmc import calculate_markov_chain, random_walk


class TestCalculateMarkovChain(unittest.TestCase):
    def test_basic(self):
        '''calculate_markov_chain: check for expected result from model input'''
        data = pd.DataFrame(data=[1,2,3,2,3,1])
        self.assertEqual(calculate_markov_chain(data), [[1/3, 2/3],[1,0]])

    def test_all_states_present(self):
        '''calculate_markov_chain: check that function works properly when all
        elements of the matrix are non-zero'''
        data = pd.DataFrame(data=[1,2,3,7,5,4,6])
        self.assertEqual(calculate_markov_chain(data), [[2/3, 1/3], [1/2, 1/2]])
    
    def test_always_gain(self):
        '''calculate_markov_chain: edge case when price data always increases (divide by 0)'''
        data = pd.DataFrame(data=[1,2,3,4,5,6,7])
        self.assertEqual(calculate_markov_chain(data), [[1,0],[0,0]])

    def test_always_lose(self):
        '''calculate_markov_chain: edge case when price data always decreases (divide by 0)'''
        data = pd.DataFrame(data=[7,6,5,4,3,2,1])
        self.assertEqual(calculate_markov_chain(data), [[0,0],[0,1]])

    def test_no_movement(self):
        '''calculate_markov_chain: edge case where the data never increases or decreases'''
        data = pd.DataFrame(data=[1,1,1,1,1,1,1])
        # current expected behavior: treated as a gain
        self.assertEqual(calculate_markov_chain(data), [[1,0],[0,0]])
        

class TestRandomWalk(unittest.TestCase):
    def test_always_gain(self):
        '''random_walk: edge case where markov chain has form [[1,0],[0,0]] '''
        depth = 100
        pts = random_walk([[1,0], [0,0]], depth, 0)

        # we cannot directly compare python lists, so we compare elementwise instead
        verification = list(map(lambda x: x[0] == x[1], zip(pts, range(1, depth+1))))
        self.assertTrue(all(verification))

    def test_always_loss(self):
        '''random_walk: edge case where markov chain has form [[0,0], [0,1]]'''
        depth = 100
        pts = random_walk([[0,0], [0,1]], depth, 1)

        verification = list(map(lambda x: x[0] == x[1], zip(pts, range(-1, -depth-1, -1))))
        self.assertTrue(all(verification))
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
