################################################################################
#
# File:    strategy.py
# Author:  Michael Cooney
# Purpose: define miscellaneous functions to be used for analysis
#
################################################################################

import datetime as dt
import pandas as pd
from security import Security


def n_day_sma(security: Security, num_days: int, window_size: int) -> pd.DataFrame:
    # start_day = dt.datetime.today() - dt.timedelta(days=num_days)
    # hist = security.get_history(start_day)
    hist = security.get_history()
    return hist['Close'].rolling(window=window_size, min_periods=window_size).mean()


# def n_day_ema(security: Security, num_days: int, window_size: int, smoothing: int) -> pd.DataFrame:
def n_day_ema(security: Security, window_size: int) -> pd.DataFrame:
    # start_day = dt.datetime.today() - dt.timedelta(days=num_days)
    # hist = security.get_history(start_day)

    hist = security.get_history()
    multiplier = 2 / (1 + window_size)
    # initial ema is sma
    init_ema = hist['Close'].iloc[:window_size].mean()

    for idx, row in hist.iloc[window_size:].iterrows():
        val_t = row.values[0]
        ema = (val_t * multiplier) + (init_ema * (1-multiplier))
        hist.loc[idx, 'ema'] = ema
        init_ema = ema

    return hist['ema']


# def ema(df, span):
#    ...:     multiplier = 2/(1+span)
#    ...:     init_sma = df['Close'].iloc[:span].mean()
#    ...:     for idx, row in df.iloc[span:].iterrows():
#    ...:         val_t = row.values[0]
#    ...:         ema = (val_t * multiplier) + (init_sma * (1-multiplier))
#    ...:         df.loc[idx, 'ema'] = ema
#    ...:         init_sma = ema
#    ...:     print(df)
