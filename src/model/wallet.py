from collections import namedtuple
from datetime import datetime
from decimal import *

from model.trade import Trade, TradeType

WalletData = namedtuple('WalletData', 'qty_buy total_buy qty_sell total_sell qty pru pnl total_pnl',
                        defaults=(
                            Decimal('0.0'), Decimal('0.0'), Decimal('0.0'), Decimal('0.0'), Decimal('0.0'),
                            Decimal('0.0'),
                            Decimal('0.0'), Decimal('0.0')))


class Wallet:
    def __init__(self, id: int = None, name: str = 'Wallet ' + str(datetime.now()),
                 date: datetime = datetime.now()):
        self.id = id
        self.name = name
        self.date = date
        self.assets = {}

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, val: int):
        if val is not None and type(val) is not int:
            raise ValueError("L'id doit être un entier.")
        self._id = val

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        self._name = val

    @property
    def date(self) -> datetime:
        return self._date

    @date.setter
    def date(self, val: datetime):
        if type(val) is not None and type(val) is not datetime:
            raise ValueError("La doit être une date valide.")
        self._date = val

    @staticmethod
    def import_trades(trades: list[Trade]):
        asset_wallet = {}

        if len(trades) > 0:
            wallet = Wallet.get_new_wallet()
            for trade in trades:
                # print()
                # print(trade)
                buy_asset, sell_asset = trade.get_assets()
                fee_asset = trade.fee_asset
                if buy_asset not in asset_wallet:
                    asset_wallet[buy_asset] = WalletData()
                if sell_asset not in asset_wallet:
                    asset_wallet[sell_asset] = WalletData()
                if fee_asset not in asset_wallet:
                    asset_wallet[fee_asset] = WalletData()
                if trade.type == TradeType.BUY:
                    qty_buy = Decimal(asset_wallet[buy_asset].qty_buy + trade.qty)
                    total_buy = Decimal(asset_wallet[buy_asset].total_buy + trade.total)
                    qty = Decimal(asset_wallet[buy_asset].qty + trade.qty)
                    pru = Decimal(((asset_wallet[buy_asset].qty * asset_wallet[
                        buy_asset].pru) + trade.total) / qty if qty != 0.0 else 0.0)
                    asset_wallet[buy_asset] = WalletData(qty_buy,
                                                         total_buy,
                                                         asset_wallet[buy_asset].qty_sell,
                                                         asset_wallet[buy_asset].total_sell,
                                                         qty,
                                                         pru,
                                                         0,
                                                         asset_wallet[buy_asset].total_pnl)
                    asset_wallet[sell_asset] = WalletData(asset_wallet[sell_asset].qty_buy,
                                                          asset_wallet[sell_asset].total_buy,
                                                          asset_wallet[sell_asset].qty_sell,
                                                          asset_wallet[sell_asset].total_sell,
                                                          asset_wallet[sell_asset].qty - trade.total,
                                                          asset_wallet[sell_asset].pru,
                                                          asset_wallet[sell_asset].pnl,
                                                          asset_wallet[sell_asset].total_pnl)

                elif trade.type == TradeType.SELL:
                    qty_sell = asset_wallet[buy_asset].qty_sell + trade.qty
                    total_sell = asset_wallet[buy_asset].total_sell + trade.total
                    qty = Decimal(asset_wallet[buy_asset].qty - trade.qty)
                    pnl = trade.total - (trade.qty * asset_wallet[buy_asset].pru)
                    total_pnl = asset_wallet[buy_asset].total_pnl + pnl
                    asset_wallet[buy_asset] = WalletData(asset_wallet[buy_asset].qty_buy,
                                                         asset_wallet[buy_asset].total_buy,
                                                         qty_sell,
                                                         total_sell,
                                                         qty,
                                                         asset_wallet[buy_asset].pru if qty != 0 else 0,
                                                         pnl,
                                                         total_pnl)
                    asset_wallet[sell_asset] = WalletData(asset_wallet[sell_asset].qty_buy,
                                                          asset_wallet[sell_asset].total_buy,
                                                          asset_wallet[sell_asset].qty_sell,
                                                          asset_wallet[sell_asset].total_sell,
                                                          asset_wallet[sell_asset].qty + trade.total,
                                                          asset_wallet[sell_asset].pru,
                                                          asset_wallet[sell_asset].pnl,
                                                          asset_wallet[sell_asset].total_pnl)
                # fees
                asset_wallet[fee_asset] = WalletData(asset_wallet[fee_asset].qty_buy,
                                                     asset_wallet[fee_asset].total_buy,
                                                     asset_wallet[fee_asset].qty_sell,
                                                     asset_wallet[fee_asset].total_sell,
                                                     asset_wallet[fee_asset].qty - trade.fee,
                                                     asset_wallet[fee_asset].pru,
                                                     asset_wallet[fee_asset].pnl,
                                                     asset_wallet[fee_asset].total_pnl)

                # print(buy_asset, asset_wallet[buy_asset].qty)
                # print(sell_asset, asset_wallet[sell_asset])
                # print(fee_asset, asset_wallet[fee_asset])

        return asset_wallet

    @staticmethod
    def import_trades_from_csv_file(filename: str):
        trades = Trade.get_trades_from_csv_file(filename)
        return Wallet.import_trades(trades)

    @staticmethod
    def get_new_wallet():
        return Wallet()
