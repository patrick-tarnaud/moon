import csv
import os
import sqlite3
from datetime import datetime
from decimal import *
from enum import Enum
from typing import Union

from exceptions.exceptions import EntityNotFoundError, AssetNotFoundError
from db.db import ConnectionDB


# enums
class TradeType(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class TradeOrigin(Enum):
    BINANCE = 'BINANCE'
    OTHER = 'OTHER'


# db requests
SQL_INSERT_TRADE = """insert into trade(id_wallet, pair, type, qty, price, total, date, fee, fee_asset, origin_id, 
origin) values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?); """
SQL_UPDATE_TRADE = """update trade set id_wallet = ?, pair = ?, type  = ?, qty = ?, price = ?, total = ?, date = ?, 
fee = ?, fee_asset = ?, origin_id = ?, origin = ? where id = ? """
SQL_SELECT_READ_TRADE = """select id, id_wallet, pair, type, qty, price, total, date, fee, fee_asset, origin_id, 
origin from trade where id=? """
SQL_SELECT_FIND_TRADE = "select id, id_wallet, pair, type, qty, price, total, date, fee, fee_asset, origin_id, " \
                        "origin from trade "
SQL_DELETE_TRADE = "delete from trade where id=?"

SQL_SELECT_PAIRS = 'select distinct pair from trade order by pair'

# indexes in CSV file from Binance for import
BINANCE_CSV_INDEX_DATE = 0
BINANCE_CSV_INDEX_PAIR = 1
BINANCE_CSV_INDEX_TRADE_TYPE = 2
BINANCE_CSV_INDEX_PRICE = 3
BINANCE_CSV_INDEX_QTY = 4
BINANCE_CSV_INDEX_TOTAl = 5
BINANCE_CSV_INDEX_FEE = 6
BINANCE_CSV_INDEX_FEE_ASSET = 7

# CURRENCY_LIST = ('EUR', 'USDT')
ASSET_LIST = (
    'BTC', 'ETH', 'BNB', 'HOT', 'SXP', 'DOT', 'ADA', 'CHZ', 'SOL', 'FIL', 'EGLD', 'CAKE', 'EOS', 'PERL', 'UNI', 'XLM',
    'MANA', 'XRP', 'AVAX', 'HNT', 'DOGE', 'BTT', 'INJ', 'KAVA', 'LTC', 'LINK', 'EUR', 'USDT')


class Trade:

    def __init__(self,
                 id_: Union[int, None],
                 id_wallet: int,
                 pair: str,
                 type_: Union[TradeType, str],
                 qty: Decimal,
                 price: Decimal,
                 total: Decimal,
                 date: Union[datetime, str] = datetime.now(),
                 fee: Decimal = Decimal('0.0'),
                 fee_asset: str = '',
                 origin_id: str = '',
                 origin: TradeOrigin = TradeOrigin.OTHER):
        self.id = id_
        self.id_wallet = id_wallet
        self.pair = pair
        self.type = type_
        self.qty = qty
        self.price = price
        self.total = total if total else qty * price
        self.date = date
        self.fee = fee
        self.fee_asset = fee_asset
        self.origin_id = origin_id
        self.origin = origin

    def __repr__(self):
        return f'Trade(id={self.id}, id_wallet={self.id_wallet}, pair={self.pair}, type={self.type}, qty={self.qty}, ' \
               f'price={self.price}, total={self.total}, date={self.date}, fee={self.fee}, fee_asset={self.fee_asset},' \
               f'origin_id={self.origin_id}, origin={self.origin})'

    def __eq__(self, other):
        if not isinstance(other, Trade):
            return False
        return (
                self.id_wallet == other.id_wallet and self.pair == other.pair and self.type == other.type and
                self.qty == other.qty and self.price == other.price and self.total == other.total
                and self.date == other.date and self.fee == other.fee and self.fee_asset == other.fee_asset and
                self.origin_id == other.origin_id and self.origin == other.origin)

    def __hash__(self):
        return hash((self.id_wallet, self.pair, self.qty, self.price, self.total, self.fee, self.fee_asset,
                     self.origin_id, self.origin))

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, val: int):
        if val is not None and type(val) is not int:
            raise ValueError("L'id doit être de type int")
        self._id = val

    @property
    def id_wallet(self) -> int:
        return self._id_wallet

    @id_wallet.setter
    def id_wallet(self, val: int):
        if val is not None and type(val) is not int:
            raise ValueError("L'id du portefeuille doit être de type int")
        self._id_wallet = val

    @property
    def pair(self) -> str:
        return self._pair

    @pair.setter
    def pair(self, val: str):
        self._pair = str(val) if val is not None else None

    @property
    def type(self) -> TradeType:
        return self._type

    @type.setter
    def type(self, val: TradeType):
        self._type = TradeType(val) if val is not None else None

    @property
    def qty(self) -> Decimal:
        return self._qty

    @qty.setter
    def qty(self, val: Decimal):
        if val is not None and not isinstance(val, Decimal):
            self._qty = Decimal(str(val))
        else:
            self._qty = val

    @property
    def price(self) -> Decimal:
        return self._price

    @price.setter
    def price(self, val: Decimal):
        if val is not None and not isinstance(val, Decimal):
            self._price = Decimal(str(val))
        else:
            self._price = val

    @property
    def total(self) -> Decimal:
        return self._total

    @total.setter
    def total(self, val: Decimal):
        if val is not None and not isinstance(val, Decimal):
            self._total = Decimal(str(val))
        else:
            self._total = val

    @property
    def date(self) -> datetime:
        return self._date

    @date.setter
    def date(self, val: datetime):
        if val is not None and type(val) is not datetime and type(val) is not str:
            raise ValueError('La date doit être de type Date ou Str au format %Y-%m-%d %H:%M:%S')
        if val is not None:
            self._date = val if type(val) is datetime else datetime.strptime(val, '%Y-%m-%d %H:%M:%S')
        else:
            self._date = None

    @property
    def fee(self) -> Decimal:
        return self._fee

    @fee.setter
    def fee(self, val: Decimal):
        if val is not None and not isinstance(val, Decimal):
            self._fee = Decimal(str(val))
        else:
            self._fee = val

    @property
    def fee_asset(self) -> str:
        return self._fee_asset

    @fee_asset.setter
    def fee_asset(self, val: str):
        self._fee_asset = val

    @property
    def origin_id(self) -> str:
        return self._origin_id

    @origin_id.setter
    def origin_id(self, val: str):
        self._origin_id = val

    @property
    def origin(self) -> TradeOrigin:
        return self._origin

    @origin.setter
    def origin(self, val: TradeOrigin):
        self._origin = TradeOrigin(val) if val is not None else None

    def get_assets(self):
        buy_asset = None
        sell_asset = None
        for asset in ASSET_LIST:
            if self.pair.startswith(asset):
                buy_asset = asset
            if self.pair.endswith(asset):
                sell_asset = asset
            if buy_asset and sell_asset:
                break
        return buy_asset, sell_asset

    @staticmethod
    def filter_new_trades(id_wallet: int, trades: list['Trade']) -> list['Trade']:
        """
        Returns the trades that don't already exist in the wallet among those passed in parameters
        @:param id_wallet: wallet's id
        @:param trades: the trades to filter
        @:return: the new trades passed for the wallet
        """

        # get the interval of time for loading trades from db
        # search in db all trades in the interval
        begin_date = min(trades, key=lambda t: t.date).date
        end_date = max(trades, key=lambda t: t.date).date
        trades_in_db = Trade.find(id_wallet=id_wallet, begin_date=begin_date, end_date=end_date)

        # return difference between trades set and db set
        return sorted(list(set(trades) - set(trades_in_db)), key=lambda t: t.date)

    @staticmethod
    def import_trades(id_wallet: int, trades: list['Trade']) -> list['Trade']:
        """
        Import only new trades passed in parameter in database
        The trades already existing are ignored
        :param id_wallet: wallet's id
        :param trades: the trades to import
        :return: the saved trades
        """
        new_trades = Trade.filter_new_trades(id_wallet, trades)
        for trade in new_trades:
            trade.id_wallet = id_wallet
        Trade.save_all(new_trades)
        return new_trades

    @staticmethod
    def import_trades_from_csv_file(id_wallet: int, csv_file: str) -> list['Trade']:
        """
        Import trades from csv file

        :param id_wallet: wallet's id
        :param csv_file: teh csh filename
        :raises FileNotFoundError: if file doesn't exist
        """
        trades = Trade.get_trades_from_csv_file(csv_file)
        new_trades = Trade.import_trades(id_wallet, trades)
        return new_trades

    @staticmethod
    def find(id_wallet: int = None, pair: str = None, trade_type: TradeType = None, begin_date: datetime = None,
             end_date: datetime = None, origin: TradeOrigin = None) -> list['Trade']:
        """
        Find trades by criteria, if no parameters supplied then all trades are returns

        :param id_wallet: walle's id
        :param pair: pair to search
        :param trade_type: trade type
        :param begin_date: begin date
        :param end_date: end date
        :param origin: origin of the trade
        :returns: trades list accordingly to the criterias
        """
        req = SQL_SELECT_FIND_TRADE
        parameters = []

        # SQL request definition
        if id_wallet or pair or trade_type or begin_date or end_date or origin:
            req += ' where '
        if id_wallet:
            req += ' and id_wallet = ? ' if parameters else ' id_wallet = ? '
            parameters.append(id_wallet)
        if pair:
            if '*' in pair:
                pair = pair.replace('*', '%')
                req += ' and pair like ? ' if parameters else ' pair like ? '
            else:
                req += ' and pair = ? ' if parameters else ' pair = ? '
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
        req += ' order by date'

        ConnectionDB.get_cursor().execute(req, parameters)
        rows = ConnectionDB.get_cursor().fetchall()
        return [Trade(*row) for row in rows]

    @staticmethod
    def read(id_: int) -> 'Trade':
        """
        Returns the trade identified by the id parameter

        :param id_: trade id
        :returns: the found trade
        :raises EntityNotFoundError: if no trade found
        """
        ConnectionDB.get_cursor().execute(SQL_SELECT_READ_TRADE, (id_,))
        row = ConnectionDB.get_cursor().fetchone()
        if row is None:
            raise EntityNotFoundError(f"Le trade {id_} n'existe pas")
        t = Trade(*row)
        return t

    def save(self) -> None:
        """
        Save or update a trade (insert or update in db)

        :returns: the saved trade with its id
        """
        # update in db
        if self.id is not None:
            ConnectionDB.get_cursor().execute(SQL_UPDATE_TRADE,
                                              (self.id_wallet, self.pair, self.type.value, float(self.qty),
                                               float(self.price), float(self.total), self.date,
                                               float(self.fee),
                                               self.fee_asset,
                                               self.origin_id, self.origin.value, self.id))
        # insert in db
        else:
            cur = ConnectionDB.get_cursor().execute(SQL_INSERT_TRADE,
                                                    (self.id_wallet, self.pair, self.type.value, float(self.qty),
                                                     float(self.price), float(self.total), self.date,
                                                     float(self.fee),
                                                     self.fee_asset,
                                                     self.origin_id, self.origin.value))
            self.id = cur.lastrowid

    @staticmethod
    def save_all(trades: list['Trade']) -> None:
        """
        Save all trades passed i parameter (update or insert in db)

        :param trades: trades lsit
        """
        # transform original list to get the values of the enums (type and origin)
        update_trades = [trade for trade in trades if trade.id is not None]
        update_trades = list(map(lambda trade: (trade.id_wallet, trade.pair, trade.type.value, float(trade.qty),
                                                float(trade.price), float(trade.total), trade.date,
                                                float(trade.fee),
                                                trade.fee_asset,
                                                trade.origin_id,
                                                trade.origin.value, trade.id), update_trades))
        ConnectionDB.get_cursor().executemany(SQL_UPDATE_TRADE, update_trades)

        insert_trades = [trade for trade in trades if trade.id is None]
        insert_trades = list(map(lambda trade: (trade.id_wallet, trade.pair, trade.type.value, float(trade.qty),
                                                float(trade.price), float(trade.total), trade.date,
                                                float(trade.fee),
                                                trade.fee_asset,
                                                trade.origin_id,
                                                trade.origin.value), insert_trades))
        ConnectionDB.get_cursor().executemany(SQL_INSERT_TRADE, insert_trades)

        ConnectionDB.commit()

    def delete(self) -> None:
        """
        Delete trade
        """
        Trade.read(self.id)
        ConnectionDB.get_cursor().execute(SQL_DELETE_TRADE, (self.id,))
        ConnectionDB.commit()

    @staticmethod
    def get_pairs() -> set[str]:
        """
        Get pairs (ex BTCEUR) existing in db

        :returns: pairs
        """
        ConnectionDB.get_cursor().execute(SQL_SELECT_PAIRS)
        pairs = ConnectionDB.get_cursor().fetchall()
        # transform list of tuples in list of str value
        pairs = {pair[0] for pair in pairs}
        return pairs

    @staticmethod
    def get_trades_from_csv_file(filename: str) -> list['Trade']:
        """
        Read trades from csv file (with ';' delimiter) and return them

        :param filename: filename of the csv file with path (ie /home/patrick/Documents/Finances/binance-export-trades.csv)
        :returns: a list of Trades
        :raises FileNotFoundError: if the file doesn't exist
        """
        # loop on csv row and create a trade object for each and add it to the trades list
        trades = []
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                trades.append(Trade(None, None, row[BINANCE_CSV_INDEX_PAIR],
                                    row[BINANCE_CSV_INDEX_TRADE_TYPE],
                                    Decimal(row[BINANCE_CSV_INDEX_QTY]),
                                    Decimal(row[BINANCE_CSV_INDEX_PRICE]),
                                    Decimal(row[BINANCE_CSV_INDEX_TOTAl]),
                                    row[BINANCE_CSV_INDEX_DATE],
                                    Decimal(row[BINANCE_CSV_INDEX_FEE]),
                                    row[BINANCE_CSV_INDEX_FEE_ASSET],
                                    None,
                                    TradeOrigin.BINANCE))

        return trades
