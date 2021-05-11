from datetime import datetime
from enum import Enum


class TradeType(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class TradeOrigin(Enum):
    BINANCE = 'BINANCE'
    OTHER = 'OTHER'


BUY_ASSETS = ('EUR', 'USDT', 'BNB')


class Trade:
    def __init__(self, id: int = None, pair: str = None, type: TradeType = TradeType.BUY, qty: float = None,
                 price: float = None,
                 total: float = None, date: datetime = None,
                 fee: float = None,
                 fee_asset: str = None, origin_id: str = None, origin: TradeOrigin = None):
        self.id = id
        self.pair = pair
        self.type = type
        self.qty = qty
        self.price = price
        self.total = total
        self.date = date
        self.fee = fee
        self.fee_asset = fee_asset
        self.origin_id = origin_id
        self.origin = origin

    def __repr__(self):
        return f'Trade(id={self.id}, pair={self.pair}, type={self.type}, qty={self.qty}, price={self.price}, total={self.total}, date={self.date}, fee={self.fee}, fee_asset={self.fee_asset}, origin_id={self.origin_id}, origin={self.origin})'

    def __eq__(self, other):
        if not isinstance(other, Trade): return False
        return self.pair == other.pair and self.type == other.type and self.qty == other.qty and self.price == other.price and self.total == other.total and self.fee == other.fee and self.fee_asset == other.fee_asset and self.origin_id == other.origin_id and self.origin == other.origin

    def __hash__(self):
        return hash(
            (self.pair, self.qty, self.price, self.total, self.fee, self.fee_asset, self.origin_id, self.origin))

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, val: int):
        if val is not None and type(val) is not int: raise ValueError("L'id doit être de type int")
        self._id = val

    @property
    def pair(self) -> str:
        return self._pair

    @pair.setter
    def pair(self, val: str):
        self._pair = str(val)

    @property
    def type(self) -> TradeType:
        return self._type

    @type.setter
    def type(self, val: TradeType):
        self._type = TradeType(val)

    @property
    def qty(self) -> float:
        return self._qty

    @qty.setter
    def qty(self, val: float):
        self._qty = float(val)

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, val: float):
        self._price = float(val)

    @property
    def total(self) -> float:
        return self._total

    @total.setter
    def total(self, val: float):
        self._total = float(val)

    @property
    def date(self) -> float:
        return self._date

    @date.setter
    def date(self, val: datetime):
        if not type(val) is datetime: raise ValueError('La date doit être de type Date')
        self._date = val

    @property
    def fee(self) -> float:
        return self._fee

    @fee.setter
    def fee(self, val: float):
        self._fee = float(val)

    @property
    def fee_asset(self) -> float:
        return self._fee_asset

    @fee_asset.setter
    def fee_asset(self, val: str):
        self._fee_asset = str(val)

    @property
    def origin_id(self) -> float:
        return self._origin_id

    @origin_id.setter
    def origin_id(self, val: str):
        self._origin_id = str(val)

    @property
    def origin(self) -> TradeOrigin:
        return self._origin

    @origin.setter
    def origin(self, val: TradeOrigin):
        self._origin = TradeOrigin(val)

    @staticmethod
    def pair_to_asset(pairs: list[str]) -> set[str]:
        res = set()
        for pair in pairs:
            for ba in BUY_ASSETS:
                if pair.endswith(ba):
                    res.add(pair.removesuffix(ba))
                    break
        return res

    @staticmethod
    def get_wallet():
        pass
