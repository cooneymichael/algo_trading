################################################################################
#
# File:    strategy.py
# Author:  Michael Cooney
# Purpose: Use functions and objects to define a trading strategy
#
################################################################################


from security import Security
from monte_carlo_simulation import MonteCarloSimulation as MCS

if __name__ == '__main__':
    ewy = Security('EWY', '../Data/Data/stocks.db')
    ewy_history = ewy.get_history()
    print(ewy)
    print(ewy_history)

    ewy_mcs = MCS(ewy_history)
    simulation = ewy_mcs.monte_carlo_sim(depth=500)
    print(simulation)
    
    
