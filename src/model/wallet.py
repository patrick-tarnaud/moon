from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from decimal import *
from pprint import pprint

from model.trade import Trade, TradeType

WalletData = namedtuple('WalletData', 'qty pru currency',
                        defaults=(
                            Decimal('0.0'), Decimal('0.0'), None))

PnlData = namedtuple('PnlData', 'date asset value currency')


@dataclass
class PnlTotal:
    asset: str
    value: Decimal
    currency: str


class Wallet:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
        self.trades: list[Trade] = []
        self.assets: dict[str, WalletData] = {}
        self.pnl: list[PnlData] = []
        self.cumulative_pnl: list[PnlTotal] = []

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

    def import_trades(self, trades: list[Trade]):
        asset_wallet = {}
        pnl_data_list = []
        pnl_total_list = []

        if len(trades) > 0:
            for trade in trades:
                asset1, asset2 = trade.get_assets()
                fee_asset = trade.fee_asset

                # init structures
                if asset1 not in asset_wallet:
                    asset_wallet[asset1] = WalletData()
                if asset2 not in asset_wallet:
                    asset_wallet[asset2] = WalletData()
                if fee_asset not in asset_wallet:
                    asset_wallet[fee_asset] = WalletData()

                # BUY
                if trade.type == TradeType.BUY:
                    qty = asset_wallet[asset1].qty + trade.qty
                    pru = ((asset_wallet[asset1].qty * asset_wallet[
                        asset1].pru) + trade.total) / qty if qty != 0.0 else 0.0
                    asset_wallet[asset1] = WalletData(qty,
                                                      pru,
                                                      asset2)
                    asset_wallet[asset2] = WalletData(asset_wallet[asset2].qty - trade.total,
                                                      asset_wallet[asset2].pru,
                                                      asset_wallet[asset2].currency)
                # SELL
                elif trade.type == TradeType.SELL:
                    qty = asset_wallet[asset1].qty - trade.qty
                    pnl = trade.total - (trade.qty * asset_wallet[asset1].pru)
                    pnl_data_list.append(PnlData(trade.date, asset1, pnl, asset2))
                    pnl_total = [e for e in pnl_total_list if e.asset == asset1 and e.currency == asset2]
                    if pnl_total:
                        pnl_total[0].value += pnl
                    else:
                        pnl_total_list.append(PnlTotal(asset1, pnl, asset2))
                    asset_wallet[asset1] = WalletData(qty,
                                                      asset_wallet[asset1].pru if qty != 0 else 0,
                                                      asset2)
                    asset_wallet[asset2] = WalletData(asset_wallet[asset2].qty + trade.total,
                                                      asset_wallet[asset2].pru,
                                                      asset_wallet[asset2].currency)
                # fees
                asset_wallet[fee_asset] = WalletData(asset_wallet[fee_asset].qty - trade.fee,
                                                     asset_wallet[fee_asset].pru,
                                                     asset_wallet[fee_asset].currency)

                # logging.debug(asset1, asset_wallet[asset1].qty)
                # logging.debug(asset2, asset_wallet[asset2])
                # logging.debug(fee_asset, asset_wallet[fee_asset])

        print()
        pprint(asset_wallet)
        pprint(pnl_data_list)
        pprint(pnl_total_list)

        return asset_wallet

    def import_trades_from_csv_file(self, filename: str):
        trades = Trade.get_trades_from_csv_file(filename)
        return self.import_trades(trades)
