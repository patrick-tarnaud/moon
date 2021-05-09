import sqlite3
import os
from datetime import datetime
import copy

from model.trade import Trade, TradeType, TradeOrigin
from exceptions.exceptions import EntityNotFoundError

# get the DB from environment variable 'db'
# if db var env doesn't exist then pass, a connection will be provided on the dunder init
try:
    MOON_DB = os.environ['db']
except:
    pass

SQL_INSERT_TRADE = "insert into trade(pair, type, qty, price, total, date, fee, fee_asset, origin_id, origin) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
SQL_UPDATE_TRADE = "update trade set pair = ?, type  = ?, qty = ?, price = ?, total = ?, date = ?, fee = ?, fee_asset = ?, origin_id = ?, origin = ? where id = ?"
SQL_SELECT_READ_TRADE = "select * from trade where id=?"
SQL_SELECT_FIND_TRADE = "select * from trade"
SQL_DELETE_TRADE = "delete from trade where id=?"

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


class TradeDB:
    """
    Use for database acess
    """

    def __init__(self, conn=None):
        if conn is None:
            self.conn = sqlite3.connect(MOON_DB)
        else:
            self.conn = conn
        self.cur = self.conn.cursor()

    def find(self, pair: str = None, trade_type: TradeType = None, begin_date: datetime = None,
             end_date: datetime = None, origin: str = None) -> list[Trade]:
        req = SQL_SELECT_FIND_TRADE
        parameters = []
        if pair or trade_type or begin_date or end_date or origin: req += ' where '
        if pair:
            req += ' pair = ? '
            parameters.append(pair)
        if trade_type:
            req += ' and type = ? ' if parameters else ' type = ? '
            parameters.append(trade_type.value)
        if begin_date:
            req += ' and date >= ? ' if parameters else ' date >= ? '
            parameters.append(begin_date)
        if end_date:
            req += ' and date <= ? ' if parameters else ' date <= ? '
            parameters.append(end_date)
        if origin:
            req += ' and origin = ? ' if parameters else ' origin = ? '
            parameters.append(origin.value)
        self.cur.execute(req, parameters)
        rows = self.cur.fetchall()
        trades = []
        for row in rows:
            trades.append(Trade(row[SQL_SELECT_INDEX_ID], row[SQL_SELECT_INDEX_PAIR],
                                TradeType.BUY if row[SQL_SELECT_INDEX_TYPE] == 'BUY' else TradeType.SELL,
                                row[SQL_SELECT_INDEX_QTY], row[SQL_SELECT_INDEX_PRICE], row[SQL_SELECT_INDEX_TOTAL],
                                datetime.strptime(row[SQL_SELECT_INDEX_DATE], '%Y-%m-%d %H:%M:%S'),
                                row[SQL_SELECT_INDEX_FEE],
                                row[SQL_SELECT_INDEX_FEE_ASSET],
                                row[SQL_SELECT_INDEX_ORIGIN_ID],
                                TradeOrigin.BINANCE if row[
                                                           SQL_SELECT_INDEX_ORIGIN] == 'BINANCE' else TradeOrigin.OTHER))
        return trades

    def read(self, id: int) -> Trade:
        """
        Returns the trade identified by the id parameter

        :param id: trade id
        :return: the found trade
        :raises EntityNotFoundError: if no trade found
        """
        self.cur.execute(SQL_SELECT_READ_TRADE, (id,))
        row = self.cur.fetchone()
        if row is None:
            raise EntityNotFoundError(f"Le trade {id} n'existe pas")
        return Trade(row[SQL_SELECT_INDEX_ID], row[SQL_SELECT_INDEX_PAIR],
                     TradeType.BUY if row[SQL_SELECT_INDEX_TYPE] == 'BUY' else TradeType.SELL,
                     row[SQL_SELECT_INDEX_QTY], row[SQL_SELECT_INDEX_PRICE], row[SQL_SELECT_INDEX_TOTAL],
                     datetime.strptime(row[SQL_SELECT_INDEX_DATE], '%Y-%m-%d %H:%M:%S'), row[SQL_SELECT_INDEX_FEE],
                     row[SQL_SELECT_INDEX_FEE_ASSET],
                     row[SQL_SELECT_INDEX_ORIGIN_ID],
                     TradeOrigin.BINANCE if row[SQL_SELECT_INDEX_ORIGIN] == 'BINANCE' else TradeOrigin.OTHER)

    def save(self, trade: Trade) -> Trade:
        """
        Save or update a trade (insert or update in db)
        :param trade: the trade to save
        :return: the saved trade with its id
        """
        new_trade = copy.deepcopy(trade)
        if trade.id is None:
            cur = self.cur.execute(SQL_INSERT_TRADE, [trade.pair, trade.type.value, trade.qty,
                                                      trade.price, trade.total, trade.date, trade.fee, trade.fee_asset,
                                                      trade.origin_id, trade.origin.value])
            new_trade.id = cur.lastrowid
        else:
            self.cur.execute(SQL_UPDATE_TRADE, [trade.pair, trade.type.value, trade.qty,
                                                trade.price, trade.total, trade.date, trade.fee, trade.fee_asset,
                                                trade.origin_id, trade.origin.value, trade.id])
        self.conn.commit()
        return new_trade

    def save_all(self, trades: list[Trade]) -> None:
        newTrades = list(map(lambda trade: (trade.pair, trade.type.value, trade.qty,
                                            trade.price, trade.total, trade.date, trade.fee, trade.fee_asset,
                                            trade.origin_id,
                                            trade.origin.value), trades))
        self.cur.executemany(SQL_INSERT_TRADE, newTrades)
        self.conn.commit()

    def delete(self, id):
        self.read(id)
        self.cur.execute(SQL_DELETE_TRADE, (id,))
        self.conn.commit()

    def __del__(self):
        self.cur.close()
        self.conn.close()
