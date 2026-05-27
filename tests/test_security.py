################################################################################
#
# File:    test_security.py
# Author:  Michael Cooney
# Purpose: Define the Security class that will be used to hold, retrieve, and
#          update information about stocks and ETFs.
#
################################################################################

import datetime as dt
import numpy as np
import pandas as pd
import sqlite3
import unittest
from unittest.mock import Mock, MagicMock, call
import yfinance as yf

from errors import NoNewDataError, InvalidDateFormatError
import security as security_module
from security import Security



class TestGetHistory(unittest.TestCase):
    def setUp(self):
        self.security = Security('TEST', 'fake/db/path')


        ################################################################################
        # Mock pandas
        ################################################################################

        self.mock_history = pd.DataFrame(columns=['Datetime', 'Close'], \
                                         data=[[np.datetime64('2025-05-26T04:00:00'), 1.00], \
                                               [np.datetime64('2025-05-27T04:00:00'), 5.00]])
        self.mock_history.set_index('Datetime', inplace=True)

        self.mock_pandas = MagicMock(spec=pd)
        self.mock_pandas.read_sql.return_value = self.mock_history
        
        self._orig_pd = security_module.pd
        security_module.pd = self.mock_pandas


        ################################################################################
        # Mock sqlite3
        ################################################################################

        self.mock_sqlite3 = MagicMock(spec=sqlite3)
        self.mock_con = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_cursor_exec = MagicMock()
        
        # the mock sqlite3 connect method returns the mock con
        self.mock_sqlite3.connect.return_value = self.mock_con

        # the mock con returns the mock cursor
        self.mock_con.cursor.return_value = self.mock_cursor

        self.mock_cursor.execute.return_value = self.mock_cursor
        self.mock_cursor.fetchone.return_value = 'Mock con.cur.execute.fetchon function chain called'

        # replace the module sqlite3 con with our mock con
        self._orig_sqlite3 = security_module.sqlite3
        security_module.sqlite3 = self.mock_sqlite3


    def tearDown(self):
        security_module.sqlite3 = self._orig_sqlite3
        security_module.pd = self._orig_pd


    def test_self_history_is_none(self):
        '''Security.get_history: self.history is none and we need to fetch from db'''

        # preliminary checks
        self.assertIsNone(self.security.history)
        self.assertIsNone(self.security.history_start)

        history = self.security.get_history(dt.datetime.fromisoformat('2025-01-01'))
        
        self.assertFalse(type(history) == InvalidDateFormatError)
        self.mock_pandas.read_sql.assert_called_with('SELECT Datetime, Close FROM History WHERE SecurityId =\
        (SELECT SecurityId FROM Securities WHERE SecurityTicker = \'TEST\') AND Datetime > 2025-01-01;', \
        self.mock_con, index_col='Datetime')

        self.assertIsNone(pd.testing.assert_frame_equal(self.security.history, self.mock_history))
        self.assertTrue(self.security.history_start == '2025-05-26')
        return

    
    def test_request_earlier_date(self):
        '''Security.get_history: self.history is not none but we need to fetch
        earlier data from db'''

        preliminary_mock_data = pd.DataFrame(columns=['Datetime', 'Close'], data=[['2026-01-01', 1.00], ['2026-01-02', 5.00]])
        preliminary_mock_data.set_index('Datetime')
        self.security.history_start = '2026-01-01'
        self.security.history = preliminary_mock_data

        # preliminary checks
        self.assertIsNone(pd.testing.assert_frame_equal(self.security.history, preliminary_mock_data))
        self.assertTrue(self.security.history_start == '2026-01-01')
        
        history = self.security.get_history(dt.datetime.fromisoformat('2025-01-01'))

        self.assertFalse(type(history) == InvalidDateFormatError)
        self.mock_pandas.read_sql.assert_called_with('SELECT Datetime, Close FROM History WHERE SecurityId =\
        (SELECT SecurityId FROM Securities WHERE SecurityTicker = \'TEST\') AND Datetime > 2025-01-01 AND Datetime < 2026-01-01;',\
        self.mock_con, index_col='Datetime')
        self.mock_pandas.concat.assert_called_with([self.mock_history, preliminary_mock_data])
        self.assertTrue(self.security.history_start == '2025-01-01')
        return


    def test_history_already_gathered(self):
        '''Security.get_history: self.history has already been fetched from the
        db and we only need to return a subset of it'''

        self.security.history = self.mock_history
        self.security.history_start = '2025-01-01'
        
        history = self.security.get_history(dt.datetime.fromisoformat('2025-02-02'))

        self.assertFalse(type(history) == InvalidDateFormatError)
        self.mock_pandas.read_sql.assert_not_called()
        self.assertIsNone(pd.testing.assert_frame_equal(history, self.mock_history))
        return


    def test_history_already_gathered_start_is_none(self):
        '''Security.get_history: self.history has alredy been fetched from the
        db and start is None, so we need to return the entire history property'''

        self.security.history = self.mock_history
        self.security.history_start = '2025-01-01'

        history = self.security.get_history()

        self.assertFalse(type(history) == InvalidDateFormatError)
        self.mock_pandas.read_sql.assert_not_called()
        self.assertIsNone(pd.testing.assert_frame_equal(history, self.mock_history))        
        return


    def test_invalid_date_format(self):
        '''Security.get_history: user did not pass a datetime object as the argument
        so we should return a non-breaking error'''

        history = self.security.get_history('2025-01-01')

        self.assertTrue(type(history) == InvalidDateFormatError)
        self.mock_pandas.read_sql.assert_not_called()
        return


class TestFetchUpdatedData(unittest.TestCase):
    def setUp(self):
        '''Security.fetch_updated_data: test'''
        self.security = Security('TEST', 'fake/db/path')

        # create a fake date that we will use for 'today'
        self.mock_today_date = dt.datetime(2025, 5, 4, 16, 0, 0)

        # subclass the dt.datetime class to return a valid datetime with the mock date
        class MockDatetime(dt.datetime):
            # def __init__(self, dt):
            #     today = MagicMock(return_value=dt)
            _fixed  = self.mock_today_date
            today = MagicMock(return_value=_fixed)

        # mock the modules needed to complete the function call chain
        self.mock_dt_module = MagicMock()
        self.mock_dt_module.datetime = MockDatetime

        # save the original datetime module for teardown, replace the original
        # with the mock 
        self._orig_dt = security_module.dt
        security_module.dt = self.mock_dt_module
        

        ################################################################################
        # repeat the above for the sqlite3 connection
        ################################################################################

        self.mock_sqlite3 = MagicMock(spec=sqlite3)
        self.mock_con = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_cursor_exec = MagicMock()
        
        # the mock sqlite3 connect method returns the mock con
        self.mock_sqlite3.connect.return_value = self.mock_con

        # the mock con returns the mock cursor
        self.mock_con.cursor.return_value = self.mock_cursor

        # the sql code being tested: cur.execute(...).fetchone()
        # execute returns an instance of cursor here, so we need to mock it and
        # redirect its return to the mock cursor, otherwise it will be none and
        # our mock will not work
        self.mock_cursor.execute.return_value = self.mock_cursor
        self.mock_cursor.fetchone.return_value = 'Mock con.cur.execute.fetchon function chain called'

        # replace the module sqlite3 con with our mock con
        self._orig_sqlite3 = security_module.sqlite3
        security_module.sqlite3 = self.mock_sqlite3


        ################################################################################
        # repeat the above for the yfinance module
        ################################################################################

        mock_yf_data = pd.DataFrame(columns = ['Date', 'Open', 'High', 'Low', \
                                               'Close', 'Adj Close', 'Volume', \
                                               'Dividends', 'Stock Splits'], \
                                    data = [['2025-05-01', 182.50, 184.12, 180.10, 183.04, 183.04, 34163779, 0.00, 0.00],
                                            ['2025-05-02', 184.10, 185.07, 183.29, 183.39, 183.39, 41386755, 0.00, 0.00],
                                            ['2025-05-05', 183.75, 186.05, 181.83, 181.92, 181.92, 44187566, 0.25, 0.00],
                                            ['2025-05-06', 185.20, 188.20, 184.28, 184.99, 184.99, 22951921, 0.00, 0.00],
                                            ['2025-05-07', 186.00, 187.41, 184.45, 185.73, 185.73, 25863186, 0.00, 0.00],
                                            ['2025-05-08', 184.90, 187.24, 184.12, 185.03, 185.03, 27891769, 0.00, 0.00]])
        mock_yf_data.set_index('Date', inplace=True)

        self.mock_yf = MagicMock(spec=yf)
        self.mock_yf_ticker = MagicMock()
        self.mock_yf.Ticker.return_value = self.mock_yf_ticker

        # self.mock_ticker_history = MagicMock()
        self.mock_yf_ticker.history.return_value = mock_yf_data

        # save original and replace with mock
        self._orig_yf = security_module.yf
        security_module.yf = self.mock_yf

        return

    
    def tearDown(self):
        security_module.dt = self._orig_dt
        security_module.sqlite3 = self._orig_sqlite3
        security_module.yf = self._orig_yf

        
    def test_fetch_data_no_start_date(self):
        '''Security.fetch_updated_data: check if the function retrieves new data
        when Security.start_date is not set'''

        self.mock_cursor.fetchone.side_effect = [['2025-05-01'], ['1']]
        self.security.fetch_updated_data()
        
        self.mock_cursor.execute.assert_any_call('SELECT Datetime FROM History WHERE SecurityId = \
            (SELECT SecurityId FROM Securities WHERE SecurityTicker = \'TEST\')\
            ORDER BY Datetime DESC LIMIT 1;')
        self.mock_yf_ticker.history.assert_called_once()
        self.mock_cursor.execute.assert_any_call('SELECT SecurityId FROM Securities WHERE \
            SecurityTicker = \'TEST\'')
        self.mock_con.commit.assert_called_once()
        self.assertIsNone(self.security.history)
        self.assertIsNone(self.security.history_start)
        return

    
    def test_fetch_data_with_start_date(self):
        '''Security.fetch_updated_data: check if the function retrieves subset of
        new data when Security.start_date is set'''

        self.security.history = pd.DataFrame(columns = ['Date', 'Close'],\
                                    data = [['2025-04-01', 177.46],
                                            ['2025-04-02', 180.78],
                                            ['2025-04-03', 178.01],
                                            ['2025-04-04', 180.12]])
        self.security.history.set_index('Date', inplace=True)
        self.security.history_start = '2025-04-01'
        self.security.fetch_updated_data()


        # Assertions
        correct_history = pd.DataFrame(columns = ['Date', 'Close'],\
                                       data = [['2025-04-01', 177.46],
                                               ['2025-04-02', 180.78],
                                               ['2025-04-03', 178.01],
                                               ['2025-04-04', 180.12],
                                               ['2025-05-01', 183.04],
                                               ['2025-05-02', 183.39],
                                               ['2025-05-05', 181.92],
                                               ['2025-05-06', 184.99],
                                               ['2025-05-07', 185.73],
                                               ['2025-05-08', 185.03]])
        correct_history.set_index('Date', inplace=True)



        assert call('SELECT Datetime FROM History WHERE SecurityId = \
            (SELECT SecurityId FROM Securities WHERE SecurityTicker = \'TEST\')\
            ORDER BY Datetime DESC LIMIT 1;') not in self.mock_cursor.execute.mock_calls
        self.mock_yf_ticker.history.assert_called_once()
        self.mock_cursor.execute.assert_any_call('SELECT SecurityId FROM Securities WHERE \
            SecurityTicker = \'TEST\'')
        self.mock_con.commit.assert_called_once()

        self.assertIsNone(pd.testing.assert_frame_equal(self.security.history, correct_history))
        return
    

    def test_fetch_data_saturday_and_thursday(self):
        '''Security.fetch_updated_data: check if the function retrieves new data
        when the last updated date is Thursday and today is Saturday'''
        
        self.mock_cursor.fetchone.side_effect = [['2025-05-01'], ['1']]
        self.mock_dt_module.datetime.today.return_value = dt.datetime(2025, 5, 3, 12, 0, 0)
        self.security.fetch_updated_data()

        # assertions
        self.mock_cursor.execute.assert_any_call('SELECT Datetime FROM History WHERE SecurityId = \
            (SELECT SecurityId FROM Securities WHERE SecurityTicker = \'TEST\')\
            ORDER BY Datetime DESC LIMIT 1;')
        self.mock_dt_module.datetime.today.assert_called()
        self.mock_yf_ticker.history.assert_called_once()
        self.mock_cursor.execute.assert_any_call('SELECT SecurityId FROM Securities WHERE \
            SecurityTicker = \'TEST\'')
        self.mock_con.commit.assert_called_once()

        self.assertIsNone(self.security.history)
        self.assertIsNone(self.security.history_start)
        return


    def test_fetch_data_saturday_and_friday(self):
        '''Security.fetch_updated_data: check if the function returns an error
        when the last updated date is Friday and today is Saturday'''

        self.mock_cursor.fetchone.side_effect = [['2025-05-02'], ['1']]
        self.mock_dt_module.datetime.today.return_value = dt.datetime(2025, 5, 3, 16, 0, 0)
        should_be_error = self.security.fetch_updated_data()

        self.assertTrue(type(should_be_error) == NoNewDataError)
        self.mock_cursor.execute.assert_called_once()
        self.mock_dt_module.datetime.today.assert_called()

        self.mock_yf_ticker.history.assert_not_called()
        self.mock_con.commit.assert_not_called()
        return


    def test_fetch_data_sunday_and_friday(self):
        '''Security.fetch_updated_data: check if the function returns an error
        when the last updated date is Friday and today is Sunday'''

        self.mock_cursor.fetchone.side_effect = [['2025-05-02'], ['1']]
        self.mock_dt_module.datetime.today.return_value = dt.datetime(2025, 5, 4, 12, 0, 0)
        should_be_error = self.security.fetch_updated_data()

        self.assertTrue(type(should_be_error) == NoNewDataError)
        self.mock_cursor.execute.assert_called_once()
        self.mock_dt_module.datetime.today.assert_called()

        self.mock_yf_ticker.history.assert_not_called()
        self.mock_con.commit.assert_not_called()
        return


    def test_fetch_data_holiday(self):
        '''Security.fetch_updated_data: check if the function returns an error
        when today is a holiday and timedelta is less than one'''

        self.mock_cursor.fetchone.side_effect = [['2025-07-03'], ['1']]
        self.mock_dt_module.datetime.today.return_value = dt.datetime(2025, 7, 4, 12, 0, 0)
        should_be_error = self.security.fetch_updated_data()

        self.assertTrue(type(should_be_error) == NoNewDataError)
        self.mock_cursor.execute.assert_called_once()
        self.mock_dt_module.datetime.today.assert_called()

        self.mock_yf_ticker.history.assert_not_called()
        self.mock_con.commit.assert_not_called()
        return


    def test_fetch_data_market_open(self):
        '''Security.fetch_updated_data: check if the function returns an error
        when today's market is still open and timedelta is less than one day'''

        self.mock_cursor.fetchone.side_effect = [['2025-05-01'], ['1']]
        self.mock_dt_module.datetime.today.return_value = dt.datetime(2025, 5, 2, 12, 0, 0)
        should_be_error = self.security.fetch_updated_data()

        self.assertTrue(type(should_be_error) == NoNewDataError)
        self.mock_cursor.execute.assert_called_once()
        self.mock_dt_module.datetime.today.assert_called()

        self.mock_yf_ticker.history.assert_not_called()
        self.mock_con.commit.assert_not_called()
        return


    def test_fetch_data_same_date(self):
        '''Security.fetch_updated_data: check if the function returns an error
        when today and last_date are equal'''

        self.mock_cursor.fetchone.side_effect = [['2025-05-01'], ['1']]
        self.mock_dt_module.datetime.today.return_value = dt.datetime(2025, 5, 1, 17, 0, 0)
        should_be_error = self.security.fetch_updated_data()

        self.assertTrue(type(should_be_error) == NoNewDataError)
        self.mock_cursor.execute.assert_called_once()
        self.mock_dt_module.datetime.today.assert_called()

        self.mock_yf_ticker.history.assert_not_called()
        self.mock_con.commit.assert_not_called()
        return



if __name__ == '__main__':
    unittest.main(verbosity=1)
