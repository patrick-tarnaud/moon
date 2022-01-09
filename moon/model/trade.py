import csv
from datetime import datetime
from decimal import *
from enum import Enum
from typing import Union, Any, Optional
import logging.config

from moon.exceptions.exceptions import EntityNotFoundError, BusinessError, Error
from moon.db.db import ConnectionDB

logger = logging.getLogger(__name__)


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

SQL_SELECT_INDEX_ID = 0
SQL_SELECT_INDEX_ID_WALLET = 1
SQL_SELECT_INDEX_PAIR = 2
SQL_SELECT_INDEX_TYPE = 3
SQL_SELECT_INDEX_QTY = 4
SQL_SELECT_INDEX_PRICE = 5
SQL_SELECT_INDEX_TOTAL = 6
SQL_SELECT_INDEX_DATE = 7
SQL_SELECT_INDEX_FEE = 8
SQL_SELECT_INDEX_FEE_ASSET = 9
SQL_SELECT_INDEX_ORIGIN_ID = 10
SQL_SELECT_INDEX_ORIGIN = 11

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
    'MANA', 'XRP', 'AVAX', 'HNT', 'DOGE', 'BTT', 'INJ', 'KAVA', 'LTC', 'LINK', 'EUR', 'USDT', 'WIN')


class Trade:

    def __init__(self,
                 id: Optional[int],
                 pair: str,
                 type_: TradeType,
                 qty: Decimal,
                 price: Decimal,
                 total: Optional[Decimal] = None,
                 date: Union[datetime, str] = datetime.now(),
                 fee: Decimal = Decimal('0.0'),
                 fee_asset: str = '',
                 origin_id: str = '',
                 origin: TradeOrigin = TradeOrigin.OTHER):
        self.id = id
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
        return f'Trade(id={self.id}, pair={self.pair}, type={self.type}, qty={self.qty}, ' \
               f'price={self.price}, total={self.total}, date={self.date}, fee={self.fee}, fee_asset={self.fee_asset},' \
               f'origin_id={self.origin_id}, origin={self.origin})'

    def __eq__(self, other):
        if not isinstance(other, Trade):
            return False
        return (
                self.pair == other.pair and self.type == other.type and
                self.qty == other.qty and self.price == other.price and self.total == other.total
                and self.date == other.date and self.fee == other.fee and self.fee_asset == other.fee_asset and
                self.origin_id == other.origin_id and self.origin == other.origin)

    def __hash__(self):
        return hash((self.pair, self.qty, self.price, self.total, self.fee, self.fee_asset,
                     self.origin_id, self.origin))

    def validate(self):
        errors = []
        if self.id is not None and (type(self.id) is not int or self.id < 0):
            errors.append(Error("id", "L'id doit être de type entier et supéreur à 0."))
        if not self.pair or type(self.pair) is not str:
            errors.append(Error("pair", "La paire du trade  doit être de type chaîne de caractères"))
        if self.type is None or type(self.type) is not TradeType:
            errors.append(Error("type", "Le type du trade est obligatoire et doit être BUY ou SELL."))
        if self.qty is None or type(self.qty) is not Decimal or self.qty < 0:
            errors.append(Error("qty",
                                "La quantité du trade est obligatoire et doit être un nombre décimal supérieur ou "
                                "égal à 0."))
        if self.price is None or type(self.price) is not Decimal or self.price < 0:
            errors.append(Error("price",
                                "Le prix du trade est obligatoire et doit être un nombre décimal supérieur ou égal à 0."))
        if self.total is None or type(self.total) is not Decimal or self.total < 0:
            errors.append(Error("total",
                                "Le total du trade est obligatoire et doit être un nombre décimal supérieur ou égal à "
                                "0."))
        if self.fee is None or type(self.fee) is not Decimal or self.fee < 0:
            errors.append(
                Error("fee", "La taxe du trade doit être un nombre décimal supérieur ou égal à 0."))
        if self.fee_asset is None or type(self.fee_asset) is not str:
            errors.append(Error("fee_asset",
                                "L'asset de la taxe du trade doit être une chaîne de caratères."))
        if self.origin_id is None or type(self.origin_id) is not str:
            errors.append(Error("origin_id",
                                "L'id de l'origine du trade doit être une chaîne de caratères."))
        if self.origin is None or type(self.origin) is not TradeOrigin:
            errors.append(Error("origin",
                                "L'origine du trade doit être indiqué."))
        if errors:
            raise BusinessError(errors)

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
        :param id_wallet: wallet's id
        :param trades: the trades to filter
        :return: the new trades passed for the wallet
        """

        # get the interval of time for loading trades from db
        # search in db all trades in the interval
        begin_date = min(trades, key=lambda t: t.date).date
        end_date = max(trades, key=lambda t: t.date).date
        trades_in_db = Trade.find(id_wallet=id_wallet, begin_date=begin_date, end_date=end_date) # type: ignore

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
        Trade.save_all(id_wallet, new_trades)
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
        parameters: list[Any] = []

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
        return [Trade.__convert_row_to_trade(row) for row in rows]

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
            raise EntityNotFoundError(id_)
        t = Trade.__convert_row_to_trade(row)
        return t

    @staticmethod
    def __convert_row_to_trade(row):
        return Trade(row[SQL_SELECT_INDEX_ID],
                     row[SQL_SELECT_INDEX_PAIR],
                     TradeType(row[SQL_SELECT_INDEX_TYPE]),
                     Decimal(str(row[SQL_SELECT_INDEX_QTY])),
                     Decimal(str(row[SQL_SELECT_INDEX_PRICE])),
                     Decimal(str(row[SQL_SELECT_INDEX_TOTAL])),
                     datetime.strptime(row[SQL_SELECT_INDEX_DATE], '%Y-%m-%d %H:%M:%S'),
                     Decimal(str(row[SQL_SELECT_INDEX_FEE])),
                     row[SQL_SELECT_INDEX_FEE_ASSET],
                     row[SQL_SELECT_INDEX_ORIGIN_ID],
                     TradeOrigin(row[SQL_SELECT_INDEX_ORIGIN]))

    def save(self, id_wallet: int) -> None:
        """
        Save or update a trade (insert or update in db)

        :returns: the saved trade with its id
        """
        # update in db
        if self.id is not None:
            ConnectionDB.get_cursor().execute(SQL_UPDATE_TRADE,
                                              (id_wallet, self.pair, self.type.value, float(self.qty),
                                               float(self.price), float(self.total), self.date,
                                               float(self.fee),
                                               self.fee_asset,
                                               self.origin_id, self.origin.value, self.id))
        # insert in db
        else:
            cur = ConnectionDB.get_cursor().execute(SQL_INSERT_TRADE,
                                                    (id_wallet, self.pair, self.type.value, float(self.qty),
                                                     float(self.price), float(self.total), self.date,
                                                     float(self.fee),
                                                     self.fee_asset,
                                                     self.origin_id, self.origin.value))
            self.id = cur.lastrowid

    @staticmethod
    def save_all(id_wallet: int, trades: list['Trade']) -> None:
        """
        Save all trades passed i parameter (update or insert in db)

        :param trades: trades lsit
        """
        # transform original list to get the values of the enums (type and origin)
        update_trades = [trade for trade in trades if trade.id is not None]
        update_trades = list(map(lambda trade: (id_wallet, trade.pair, trade.type.value, float(trade.qty), # type: ignore
                                                float(trade.price), float(trade.total), trade.date,
                                                float(trade.fee),
                                                trade.fee_asset,
                                                trade.origin_id,
                                                trade.origin.value, trade.id), update_trades))
        ConnectionDB.get_cursor().executemany(SQL_UPDATE_TRADE, update_trades)

        insert_trades = [trade for trade in trades if trade.id is None]
        insert_trades = list(map(lambda trade: (id_wallet, trade.pair, trade.type.value, float(trade.qty), # type: ignore
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
        Trade.read(self.id) # type: ignore
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

        :param filename: filename of the csv file with path (ie /home/patrick/Documents/Finances/binance-export-trades1.csv)
        :returns: a list of Trades
        :raises FileNotFoundError: if the file doesn't exist
        """
        # loop on csv row and create a trade object for each and add it to the trades list
        trades = []
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            for row in csv_reader:
                trades.append(Trade(None, row[BINANCE_CSV_INDEX_PAIR],
                                    TradeType(row[BINANCE_CSV_INDEX_TRADE_TYPE]),
                                    Decimal(row[BINANCE_CSV_INDEX_QTY]),
                                    Decimal(row[BINANCE_CSV_INDEX_PRICE]),
                                    Decimal(row[BINANCE_CSV_INDEX_TOTAl]),
                                    row[BINANCE_CSV_INDEX_DATE],
                                    Decimal(row[BINANCE_CSV_INDEX_FEE]),
                                    row[BINANCE_CSV_INDEX_FEE_ASSET],
                                    '',
                                    TradeOrigin.BINANCE))

        return trades
