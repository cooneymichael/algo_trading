################################################################################
#
# File:    update_securities.py
# Author:  Michael Cooney
# Purpose: Iterate over all securities and upate their price history in the DB
#
################################################################################

import logging
import pandas as pd
from pathlib import Path
from security import Security
import sqlite3
from time import sleep

# logging handler to detect delisted symbols
logger = logging.getLogger('yfinance')
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler('delisted.log')
file_handler.addFilter(lambda record: 'delisted' in record.getMessage().lower())
logger.addHandler(file_handler)


def flatten(securities: list[tuple[str]]):
    """Remove elements from tuples. Works in-place."""
    for idx, val in enumerate(securities):
        securities[idx] = val[0]
    return securities


def get_securities_list(cur: sqlite3.Cursor) -> list[str]:
    securities = cur.execute('SELECT SecurityTicker from Securities;').fetchall()
    flatten(securities)
    return securities


if __name__ == '__main__':
    db_path = Path('../../Data/Data/stocks.db')
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    securities = get_securities_list(cur)

    for security in securities:
        print(f'Fetching data for: {security}')
        sec = Security(security, db_path)
        updated = sec.fetch_updated_data()
        del sec
        # prevent rate limiting.  In the future, this should all be rewritten to
        # work as a batch process
        sleep(1)

    con.close()

logging.shutdown()
