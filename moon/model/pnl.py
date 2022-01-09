from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional, Union, Any

from moon.db.db import ConnectionDB
from moon.exceptions.exceptions import EntityNotFoundError

SQL_FIND = "select id, id_wallet, date, asset, value, currency from pnl where id_wallet = ?"
SQL_READ = "select id, id_wallet, date, asset, value, currency from pnl where id = ?"
SQL_INSERT = "insert into pnl(id_wallet, date, asset, value, currency) values(?,?,?,?,?)"
SQL_UPDATE = "update pnl set id_wallet = ?, date = ?, asset = ?, value = ? , currency = ? where id = ?"
SQL_DELETE = "delete from pnl where id = ?"

COL_ID = 0
COL_DATE = 2
COL_ASSET = 3
COL_VALUE = 4
COL_CURRENCY = 5


class Pnl:

    def __init__(self, id_: Optional[int], date: datetime, asset: str, value: Decimal, currency: str):
        self.id = id_
        self.date = date
        self.asset = asset
        self.value: Decimal
        if isinstance(value, float):
            self.value = Decimal(str(value))
        else:
            self.value = value
        self.currency = currency

    def __repr__(self):
        return f"Pnl(id={self.id}, date='{self.date}', asset='{self.asset}', value={self.value}, currency='{self.currency}')"

    def __eq__(self, other):
        if not isinstance(other, Pnl):
            return False
        return self.date == other.date and self.asset == other.asset and self.value == other.value and self.currency == other.currency

    def __lt__(self, other):
        # if self.date < other.date:
        #     return True
        # elif self.date > other.date:
        #     return False
        # if self.asset < other.asset:
        #     return True
        # elif self.asset > other.asset:
        #     return False
        # if self.value < other.value:
        #     return True
        # elif self.value > other.value:
        #     return False
        # if self.currency < other.currency:
        #     return True
        # elif self.currency > other.currency:
        #     return False
        # return False
        return self.date < other.date or self.asset == other.asset or self.value == other.value or self.currency == other.currency

    @staticmethod
    def find(id_wallet: int, asset: str = None, begin_date: datetime = None, end_date: datetime = None,
             currency: str = None) -> list['Pnl']:
        req = SQL_FIND
        parameters: list[Any] = [id_wallet]

        if asset:
            req += ' and asset = ?'
            parameters.append(asset)
        if begin_date:
            req += ' and date >= ?'
            parameters.append(begin_date)
        if end_date:
            req += ' and date <= ? '
            parameters.append(end_date)
        if currency:
            req += ' and currency = ?'
            parameters.append(currency)

        cur = ConnectionDB.get_cursor().execute(req, parameters)
        rows = cur.fetchall()
        pnl_list = []
        for row in rows:
            pnl_list.append(Pnl(row[COL_ID], row[COL_DATE], row[COL_ASSET], row[COL_VALUE], row[COL_CURRENCY]))
        return pnl_list

    @staticmethod
    def read(id_: int) -> 'Pnl':
        cur = ConnectionDB.get_cursor().execute(SQL_READ, (id_,))
        row = cur.fetchone()
        if not row:
            raise EntityNotFoundError(id_)
        return Pnl(row[COL_ID], row[COL_DATE], row[COL_ASSET], row[COL_VALUE], row[COL_CURRENCY])

    def save(self, id_wallet: int):
        if self._is_creation():
            cur = ConnectionDB.get_cursor().execute(SQL_INSERT,
                                                    (
                                                        id_wallet, self.date, self.asset, float(self.value),
                                                        self.currency))
            self.id = cur.lastrowid
        else:
            ConnectionDB.get_cursor().execute(SQL_UPDATE,
                                              (id_wallet, self.date, self.asset, float(self.value), self.currency,
                                               self.id))

    @staticmethod
    def save_all(id_wallet: int, pnl_list: list['Pnl']):
        update_list = [pnl for pnl in pnl_list if not pnl._is_creation()]
        if update_list:
            parameters: list[Any] = [(id_wallet, pnl.date, pnl.asset, float(pnl.value), pnl.currency, pnl.id) for pnl in
                                     update_list]
            ConnectionDB.get_cursor().executemany(SQL_UPDATE, parameters)

        insert_list = [pnl for pnl in pnl_list if pnl._is_creation()]
        if insert_list:
            parameters = [(id_wallet, pnl.date, pnl.asset, float(pnl.value), pnl.currency) for pnl in insert_list]
            ConnectionDB.get_cursor().executemany(SQL_INSERT, parameters)

    def delete(self):
        ConnectionDB.get_cursor().execute(SQL_DELETE, (self.id,))

    def _is_creation(self):
        return self.id is None

    @classmethod
    def load_from_csv_file(cls, filename: str) -> list['Pnl']:
        pnl_list: list[Pnl] = []
        with open(filename, 'r') as f:
            for num, line in enumerate(f):
                # skip header
                if num > 0:
                    pnl = line.split(';')
                    # pnl[3][:-1] to skip \n
                    pnl_list.append(
                        cls(None, datetime.strptime(pnl[0], '%Y-%m-%d %H:%M:%S'), pnl[1], Decimal(pnl[2]), pnl[3][:-1]))

        return pnl_list
