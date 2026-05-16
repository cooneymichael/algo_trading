import datetime as dt
import holidays
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sqlite3
import sys
import yfinance as yf

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



class Error():
    def __init__(self, message):
        self.message = message

    def __str__(self):
        # print(f'{self.error_type}: {self.message}')
        raise NotImplementedError('Child error class needs to implement this method')


class NoNewDataError(Error):
    def __init__(self, message):
        super().__init__(message)

    def __str__(self):
        print(f'NoNewDataError: f{self.message}')


class Security():
    def __init__(self, ticker: str, db_path: str):
        self.ticker = ticker
        self.db_path = db_path
        self.history = None
        self.history_start = None

        # track if db connection is open
        self.con_flag = False


    def _open_con(self) -> sqlite3.Connection:
        try:
            self.con_flag = True
            return sqlite3.connect(self.db_path)
        except Exception as e:
            self.con_flag = False
            raise e
        

    def _close_con(self, con) -> None:
        try:
            self.con_flag = False
            con.close()
        except Exception as e:
            self.con_flag = True
            raise e


    def get_history(self, start: int=None) -> pd.DataFrame:
        # we have never gotten the history for this security
        if self.history is None:
            self.history = self._get_history_from_db(start)
            self.history_start = self.history.index[0]

        # we got the history previously, but we need more history
        elif start is not None and start < self.history_start:
            new_data = self._get_history_from_db(start=start, end=self.history_start)
            self.history = pd.concat([new_data, self.history])
            self.history_start = start
        
        # we got the history previously, and we only want a subset of it now
        elif start is not None and start > self.history_start:
            return self.history.index.date > np.datetime64(start)
        
        return self.history


    def _get_history_from_db(self, start: int=None, end: int=None) -> pd.DataFrame:
        '''Helper function to retrieve information from a sqlite 3 DB'''

        con = self._open_con()

        query = f'SELECT Datetime, Close FROM History WHERE SecurityId =\
        (SELECT SecurityId FROM Securities WHERE SecurityTicker = \'{self.ticker}\')'

        if start is not None:
            query += f' AND Datetime > {str(start)}'

        if end is not None:
            query += f' AND Datetime < {str(end)}'

        query += ';'

        data = pd.read_sql(query, con, index_col='Datetime')
        self._close_con(con)

        return data


    def _is_holiday(self):
        this_year = dt.datetime.today().year
        days_closed = holidays.US(years=this_year)
        return dt.datetime.today() in days_closed
    

    def _is_market_closed(self):
        return dt.datetime.today().hour >= 15


    def _is_new_data_available(self, last_date: str) -> bool | NoNewDataError:
        '''helper function to determine if an api call should be made to an
        external data source.  Function returns a boolean.  Possible reasons
        False might be returned include data being up to date or the trading day
        not being over.'''


        today = dt.datetime.today()
        last_date = dt.datetime.fromisoformat(last_date)
        delta = today - last_date
        day_of_week = dt.datetime.today().weekday()

        # TODO: Unit test these conditions
        if day_of_week == 5 and delta.days <= 1:
            return False
        elif day_of_week == 6 and delta.days <= 2:
            return False
        elif self._is_holiday() and delta.days <= 1:
            return False
        elif not self._is_market_closed() and delta.days <= 1:
            return False
        elif last_date.date() == today.date():
            return False
        else:
            return True


    def fetch_updated_data(self) -> None:
        if self.history is not None:
            # we have already history and have the latest date
            start_date = self.history.tail(n=1).index[0]
        else:
            # we need to read it from the db
            query = f'SELECT Datetime FROM History WHERE SecurityId = \
            (SELECT SecurityId FROM Securities WHERE SecurityTicker = \'{self.ticker}\')\
            ORDER BY Datetime DESC LIMIT 1;'

            con = self._open_con()
            cur = con.cursor()
            start_date = cur.execute(query).fetchone()[0]
            self._close_con(con)

        # no need to crash the program here, just let the caller know nothing is new
        if not self._is_new_data_available(start_date):
            return NoNewDataError('New data cannot be fetched right now')
        
        try:
            security = yf.Ticker(self.ticker)
            updated_data = security.history(start=start_date, auto_adjust=False)
            
            # We do not track these values currently
            # ETFs have capital gains, stocks do not
            if 'Capital Gains' in updated_data.columns:
                updated_data.drop(['Adj Close', 'Dividends', 'Stock Splits', 'Capital Gains'], axis=1, inplace=True)
            else:
                updated_data.drop(['Adj Close', 'Dividends', 'Stock Splits'], axis=1, inplace=True)
                
            # Open interest comes from a separate API call, I don't want to implement it yet
            updated_data['OpenInt'] = 0
            updated_data.reset_index(inplace=True)
            updated_data['Date'] = updated_data.apply(lambda x: str(x['Date']).split(' ')[0], axis=1)
            updated_data.set_index('Date', inplace=True)
            
            if self.history is not None:
                # We assume we are looking only at the close data for now
                # yfinance sets 'Date' as the index for us, no need to reset index here
                self.history = pd.concat([self.history, updated_data['Close']])
                
            # need to save to db
            con = self._open_con()
            cur = con.cursor()
            
            security_id = cur.execute(f'SELECT SecurityId FROM Securities WHERE \
            SecurityTicker = \'{self.ticker}\'').fetchone()[0]
            
            updated_data['SecurityId'] = security_id
            
            # Datetime is the index, so we keep the index in itertuples
            cur.executemany('INSERT OR IGNORE INTO History \
            (Datetime, Open, High, Low, Close, Volume, OpenInt, SecurityId) \
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)', list(updated_data.itertuples()))
            con.commit()
            
            
        except Exception as e:
            raise e

        finally:
            if self.con_flag:
                self._close_con(con)
        
    def __str__(self):
        return f'Instance of Security: {self.ticker}'



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

if __name__ == '__main__':
    
    # ewy_history = get_security_history('EWY', 2012)
    # print(ewy_history)

    ewy = Security('EWY', DB_PATH)
    # ewy.fetch_updated_data()
    ewy_history = ewy.get_history(2012)
    # print(ewy)
    print(ewy_history)
    print(type(ewy_history))

    # # d = pd.DataFrame(data=[10, 10, 11, 11.5, 6.5, 3.5, 7.5, 12.5, 18.5, 13.75])
    # # d = pd.DataFrame(data=[10, 10, 11, 12.5, 7.5, 4.5, 8.5, 13.5, 19.5, 14.75])
    # dist = calculate_price_move_distribution(ewy_history)
    # mc = calculate_markov_chain(ewy_history)

    # last_price = ewy_history['Close'].tail(n=1).values[0]

    # # pts = random_walk([[2/3,1/3],[3/4, 1/4]], 1000, 0)
    # pts = monte_carlo_sim(mc, dist, last_price, 1000, 0)
    # pts = pd.Series(pts)
    # print(pts)
    # pts.plot()
    # plt.show()

