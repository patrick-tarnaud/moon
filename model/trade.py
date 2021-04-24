from datetime import datetime
from enum import Enum


class TradeType(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class TradeOrigin(Enum):
    BINANCE = 'BINANCE'


class Trade:
    def __init__(self, id: str, pair: str, type: TradeType = None, qty: float = None, price: float = None,
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
