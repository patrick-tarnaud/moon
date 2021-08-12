from decimal import Decimal
from typing import Optional, Union, Any

from exceptions.exceptions import EntityNotFoundError

from db.db import ConnectionDB

SQL_READ = "select id, asset, value, currency from pnl_total where id = ?"
SQL_FIND = "select id, asset, value, currency from pnl_total where id_wallet = ?"
SQL_INSERT = "insert into pnl_total(id_wallet, asset, value, currency) values(?,?,?,?)"
SQL_UPDATE = "update pnl_total set id_wallet = ?, asset = ?, value = ? , currency = ? where id = ?"
SQL_DELETE = "delete from pnl_total where id = ?"
SQL_DELETE_WALLET = "delete from pnl_total where id_wallet = ?"


class PnlTotal:
    id: int
    asset: str
    value: Decimal
    currency: str

    def __init__(self, id_: Optional[int], asset: str, value: Union[Decimal, float], currency: str):
        self.id = id_
        self.asset = asset
        if isinstance(value, float):
            self.value = Decimal(str(value))
        else:
            self.value = value
        self.currency = currency

    def __eq__(self, other):
        if not isinstance(other, PnlTotal):
            return False
        return self.asset == other.asset and self.value == other.value and self.currency == other.currency

    @classmethod
    def find(cls, id_wallet: int, asset: Optional[str] = None) -> list['PnlTotal']:
        req = SQL_FIND
        parameters: list[Union[int , str]] = [id_wallet]
        if asset:
            req += 'and asset = ?'
            parameters.append(asset)
        cur = ConnectionDB.get_cursor().execute(req, parameters)
        rows = cur.fetchall()
        return [cls(*row) for row in rows]

    @classmethod
    def read(cls, id_: int) -> 'PnlTotal':
        row = ConnectionDB.get_cursor().execute(SQL_READ, (id_,)).fetchone()
        if not row:
            raise EntityNotFoundError(id_)
        return cls(*row)

    def delete(self):
        ConnectionDB.get_cursor().execute(SQL_DELETE, (self.id,))

    def save(self, id_wallet: int):
        if self._is_creation():
            cur = ConnectionDB.get_cursor().execute(SQL_INSERT,
                                                    (id_wallet, self.asset, float(self.value), self.currency))
            self.id = cur.lastrowid
        else:
            ConnectionDB.get_cursor().execute(SQL_UPDATE,
                                              (id_wallet, self.asset, float(self.value), self.currency, self.id))

    @staticmethod
    def save_all(id_wallet: int, pnl_total_list: list['PnlTotal']):
        update_list = [pnl_total for pnl_total in pnl_total_list if not pnl_total._is_creation()]
        parameters: list[Any] = [(id_wallet, pnl_total.asset, float(pnl_total.value), pnl_total.currency, pnl_total.id) for
                      pnl_total in update_list]
        ConnectionDB.get_cursor().executemany(SQL_UPDATE, parameters)

        insert_list = [pnl_total for pnl_total in pnl_total_list if pnl_total._is_creation()]
        parameters = [(id_wallet, pnl_total.asset, float(pnl_total.value), pnl_total.currency) for pnl_total in
                      insert_list]
        ConnectionDB.get_cursor().executemany(SQL_INSERT, parameters)

    @staticmethod
    def delete_wallet(id_wallet: int):
        ConnectionDB.get_cursor().execute(SQL_DELETE_WALLET, (id_wallet,))

    def _is_creation(self):
        return self.id == None
