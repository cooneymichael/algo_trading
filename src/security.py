################################################################################
#
# File:    security.py
# Author:  Michael Cooney
# Purpose: Define the Security class that will be used to hold, retrieve, and
#          update information about stocks and ETFs.
#
################################################################################

import datetime as dt
import holidays
from errors import NoNewDataError, InvalidDateFormatError
import numpy as np
import pandas as pd
import sqlite3
import yfinance as yf


class Security():
    def __init__(self, ticker: str, db_path: str):
        # TODO: make db_path a path object
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


    def get_history(self, start: dt.datetime=None) -> pd.DataFrame | InvalidDateFormatError:
        '''Get price movement history, either from a database or from the security.history
        property.'''
        if start is not None and type(start) != dt.datetime:
            return InvalidDateFormatError('\'start\' parameter must datetime object')

        # we have never gotten the history for this security
        if self.history is None:
            if start is not None:
                start_date = str(start.date())
            else:
                start_date = None
            self.history = self._get_history_from_db(start_date)
            
            # date is pd.Timestamp here, not np.datetime64
            # print(type(self.history.index[0]))
            self.history_start = str(self.history.index[0])

        # we got the history previously, but we need more history
        elif start is not None and start < dt.datetime.fromisoformat(self.history_start):
            new_data = self._get_history_from_db(start=str(start.date()), end=self.history_start)
            self.history = pd.concat([new_data, self.history])
            self.history_start = str(start.date())
        
        # we got the history previously, and we only want a subset of it now
        elif start is not None and start > dt.datetime.fromisoformat(self.history_start):
            return self.history[self.history.index.date > start.date()]
        
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


if __name__ == '__main__':
    sec = Security('EWY', '../../Data/Data/stocks.db')
    sec.get_history()
