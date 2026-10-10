from collections.abc import Sequence
from dataclasses import dataclass
from errors import FailedConnectionException, FailedCursorOpenException, FailedCursorCloseException, FailedDisconnectException
from typing import Any, Protocol
import sqlite3

# todo:
# - separate connection and cursor in DataBase
# - update security.py and unit tests, etc      


class Cursor(Protocol):
    def execute(self, sql: str, parameters: Sequence[Any] = ..., /) -> Any: ...
    def fetchone(self) -> tuple[Any, ...] | None: ...
    def fetchall(self) -> list[tuple[Any, ...]]: ...
    def close(self) -> None: ...


class Connection(Protocol):
    def cursor(self) -> Cursor: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    def close(self) -> None: ...


class DataBase:
    def __init__(self, db_path: str):
        self.db_path: str = db_path
        self.con_flag: bool = False
        self.con: Connection = None
        self.cur: Cursor = None
        

    def open_con(self) -> Connection:
        try:
            self.con = sqlite3.connect(self.db_path)
            self.con_flag = True
        except Exception as e:
            self.con_flag = False
            raise FailedConnectionError(f'failed to open connection to {self.db_path}')

        return self.con


    def open_cur(self) -> Connection:
        try:
            self.cur = self.con.cursor()
        except Exception as e:
            raise FailedCursorOpenError(f'failed to instantiate cursor for {self.db_path}')
        return self.cur


    def close_con(self) -> None:
        try:
            self.con.close()
            self.con_flag = False
        except Exception as e:
            self.con_flag = True
            raise FailedDisconnectError(f'failed to disconnect from {self.db_path}')

        return None


    def close_cur(self) -> None:
        try:
            if self.con_flag:
                self.cur.close()
        except Exception as e:
            return FailedCursorCloseError(f'failed to close cursor to {self.db_path}')

        return None
        

    def is_connection_open(self) -> bool:
        return self.con_flag


    def run_query(self, query: str) -> Connection | None:
        return self.cur.execute(query)


    def run_batch_query(self, query: str, arguments: list[any]) -> Connection | None:
        return self.cur.executemany(query, list)


    def commit(self) -> None:
        self.con.commit()
        
