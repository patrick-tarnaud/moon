from datetime import datetime
from enum import Enum


class TradeType(Enum):
    SELL = 'SELL'
    BUY = 'BUY',


class TradeOrigin(Enum):
    BINANCE = 'BINANCE'


class Trade:
    def __init__(self, id: str, pair: str, type: TradeType, qty: float, price: float, total: float, date: datetime,
                 fee: float,
                 feeAsset: str, tradeOriginId: str, tradeOrigin: TradeOrigin):
        self.id = id
        self.pair = pair
        self.type = type
        self.qty = qty
        self.price = price
        self.total = total
        self.date = date
        self.fee = fee
        self.feeAsset = feeAsset
        self.tradeOriginId = tradeOriginId
        self.tradeOrigin = tradeOrigin

    def __repr__(self):
        return f'id: {self.id}, pair: {self.pair}, type: {self.type}, qty: {self.qty}, price: {self.price}, total: {self.total}, date: {self.date}, fee: {self.fee}, feeAsset: {self.feeAsset}, tradeOriginId: {self.tradeOriginId}, tradeOrigin: {self.tradeOrigin}'
