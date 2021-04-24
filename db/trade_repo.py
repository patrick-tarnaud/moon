import sqlite3
import os

from exceptions.exceptions import EntityNotFoundError
from model.trade import Trade, TradeType, TradeOrigin
from exceptions.exceptions import EntityNotFoundError

TO_THE_MOON_DB = os.environ['db']

SQL_INSERT_TRADE = "insert into trade(id, pair, type, qty, price, total, date, fee, fee_asset, origin_id, origin) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
SQL_UPDATE_TRADE = "update trade set pair = ?, type  = ?, qty = ?, price = ?, total = ?, date = ?, fee = ?, fee_asset = ?, origin_id = ?, origin = ? where id = ?"
SQL_SELECT_READ_TRADE = "select * from trade where id=?"

SQL_SELECT_INDEX_ID = 0
SQL_SELECT_INDEX_PAIR = 1
SQL_SELECT_INDEX_TYPE = 2
SQL_SELECT_INDEX_QTY = 3
SQL_SELECT_INDEX_PRICE = 4
SQL_SELECT_INDEX_TOTAL = 5
SQL_SELECT_INDEX_DATE = 6
SQL_SELECT_INDEX_FEE = 7
SQL_SELECT_INDEX_FEE_ASSET = 8
SQL_SELECT_INDEX_ORIGIN_ID = 9
SQL_SELECT_INDEX_ORIGIN = 10


class TradeRepo:
    """
    Trade Repository
    """

    def __init__(self):
        self.conn = sqlite3.connect(TO_THE_MOON_DB)
        self.cur = self.conn.cursor()

    def find(self) -> list[Trade]:
        pass

    def read(self, id: int) -> Trade:
        """
        Returns the trade identified by the id parameter

        :param id: trade id
        """
        self.cur.execute(SQL_SELECT_READ_TRADE, (id,))
        row = self.cur.fetchone()
        if row is None:
            raise EntityNotFoundError(f"Le trade {id} n'existe pas")
        return Trade(row[SQL_SELECT_INDEX_ID], row[SQL_SELECT_INDEX_PAIR],
                     TradeType.BUY if row[SQL_SELECT_INDEX_TYPE] == 'BUY' else TradeType.SELL,
                     row[SQL_SELECT_INDEX_QTY], row[SQL_SELECT_INDEX_PRICE], row[SQL_SELECT_INDEX_TOTAL],
                     row[SQL_SELECT_INDEX_DATE], row[SQL_SELECT_INDEX_FEE], row[SQL_SELECT_INDEX_FEE_ASSET],
                     row[SQL_SELECT_INDEX_ORIGIN], row[SQL_SELECT_INDEX_ORIGIN_ID])

    def save(self, trade: Trade):
        if trade.id is None:
            self.cur.execute(SQL_INSERT_TRADE, [trade.id, trade.pair, trade.type.value, trade.qty,
                                                trade.price, trade.total, trade.date, trade.fee, trade.fee_asset,
                                                trade.origin_id, trade.origin.value])
        else:
            self.cur.execute(SQL_UPDATE_TRADE, [trade.pair, trade.type.value, trade.qty,
                                                trade.price, trade.total, trade.date, trade.fee, trade.fee_asset,
                                                trade.origin_id, trade.origin.value, trade.id])
        self.conn.commit()

    def save_all(self, trades: list[Trade]):
        newTrades = list(map(lambda trade: (trade.id, trade.pair, trade.type.value, trade.qty,
                                            trade.price, trade.total, trade.date, trade.fee, trade.fee_asset,
                                            trade.origin_id,
                                            trade.origin.value), trades))
        self.cur.executemany(SQL_INSERT_TRADE, newTrades)
        self.conn.commit()

    def __del__(self):
        self.cur.close()
        self.conn.close()
