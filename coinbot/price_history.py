from __future__ import annotations
import math
import sqlite3
import datetime as dt


class Price:
    def __init__(self: Price,
                 crypto_symbol: str,
                 fiat_symbol: str,
                 value: float,
                 timestamp: int = int(dt.datetime.now().timestamp())):
        self.crypto_symbol = crypto_symbol
        self.fiat_symbol = fiat_symbol
        self.value = value
        self.timestamp = timestamp

    def __str__(self: Price) -> str:
        return f'<Price {self.currency_pair}' \
               f' ({dt.datetime.fromtimestamp(self.timestamp).ctime()}):' \
               f' {self.value}>'

    @property
    def currency_pair(self: Price) -> str:
        return f'{self.crypto_symbol}-{self.fiat_symbol}'


class PriceHistory:
    def __init__(self: PriceHistory, db_path: str, table: str):
        self.db_path = db_path
        self.table = table

    def __enter__(self: PriceHistory) -> PriceHistory:
        # Open the session
        self.session = sqlite3.connect(self.db_path)

        # Check if the prices table exists and create it if need be
        cursor = self.session.execute('SELECT * FROM sqlite_master'
                                      ' WHERE type="table"'
                                      f' AND name="{self.table}";')
        tables = cursor.fetchall()
        if(len(tables) == 0):
            self.session.execute(f'CREATE TABLE {self.table}'
                                 ' (timestamp TIMESTAMP,'
                                 ' crypto_currency char(3),'
                                 ' fiat_currency char(3),'
                                 ' value FLOAT);')
        return self

    def __exit__(self: PriceHistory,
                 etype: str,
                 evalue: str,
                 traceback: any):
        self.session.close()

    def __str__(self: PriceHistory) -> str:
        return f'{self.session}'

    def __iter__(self: PriceHistory) -> PriceHistory:
        self._cursor = self.session.execute(f'SELECT * FROM {self.table};')
        return self

    def __next__(self: PriceHistory) -> Price:
        res = self._cursor.fetchone()
        if(res is None):
            raise StopIteration
        return Price(res[1], res[2], res[3], timestamp=res[0])

    def add(self: PriceHistory, price: Price) -> None:
        self.session.execute(f'INSERT INTO {self.table} VALUES (?, ?, ?, ?)',
                             [price.timestamp,
                              price.crypto_symbol,
                              price.fiat_symbol,
                              price.value])
        self.session.commit()

    @property
    def newest(self: PriceHistory) -> Price:
        res = self.session.execute(f'SELECT * FROM {self.table}'
                                   ' ORDER BY timestamp DESC LIMIT 1;') \
                          .fetchone()
        if(res is None):
            return None
        return Price(res[1], res[2], res[3], timestamp=res[0])

    @property
    def oldest(self: PriceHistory) -> Price:
        res = self.session.execute(f'SELECT * FROM {self.table}'
                                   ' ORDER BY timestamp LIMIT 1;').fetchone()
        if(res is None):
            return None
        return Price(res[1], res[2], res[3], timestamp=res[0])

    def fuzzy(self: PriceHistory,
              delta: dt.timedelta,
              range: dt.timedelta = dt.timedelta(seconds=10),
              depth: int = 1) -> Price:
        offset = dt.datetime.now() - delta
        min = (offset - range).timestamp()
        max = (offset + range).timestamp()
        res = self.session.execute(f'SELECT * FROM {self.table}'
                                   f' WHERE timestamp >= {min}'
                                   f' AND timestamp <= {max}'
                                   ' ORDER BY timestamp LIMIT 1;').fetchall()
        if(res is None or len(res) == 0):
            if(depth > 3):
                return None
            return self.fuzzy(delta,
                              range=dt.timedelta(seconds=(range.total_seconds()
                                                 + (60 * depth))),
                              depth=depth+1)
        mid = math.ceil(len(res) / 2) - 1
        select = res[mid]
        return Price(select[1], select[2], select[3], timestamp=select[0])

    def delta(self: PriceHistory,
              delta: dt.timedelta = dt.timedelta(seconds=1)) -> float:
        oldest = self.fuzzy(delta)
        newest = self.newest
        if(oldest is None):
            return None
        print(f'Comparing against record: {oldest}')
        return round((1 - (newest.value / oldest.value)) * 100, 2)
