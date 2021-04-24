import sqlite3
from model.trade import Trade

TO_THE_MOON_DB = 'to_the_moon.db'

SQL_INSERT_TRADE = "insert into trade(id, pair, type, qty, price, total, date, fee, fee_asset, origin_id, origin) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"

class TradeRepo:
    """
    Trade Repository
    """
    def __init__(self):
        self.conn = sqlite3.connect(TO_THE_MOON_DB)
        self.cursor = self.conn.cursor()

    def find(self) -> list[Trade]:
        pass

    def save(self, trade: Trade):
            self.cursor.execute(SQL_INSERT_TRADE, [trade.id, trade.pair, trade.type.value, trade.qty,
                trade.price, trade.total, trade.date, trade.fee, trade.fee_asset, trade.origin_id, trade.origin.value])
            self.conn.commit()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

