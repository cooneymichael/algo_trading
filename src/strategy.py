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
    start_day = dt.datetime.today() - dt.timedelta(days=num_days)
    # hist = security.get_history(start_day)
    hist = security.get_history()
    return hist['Close'].rolling(window=window_size, min_periods=window_size).mean()

