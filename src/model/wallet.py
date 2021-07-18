import logging.config
from collections import namedtuple
from dataclasses import dataclass
from decimal import *
from typing import Union

from exceptions.exceptions import EntityValidateError, EntityNotFoundError
from model.trade import Trade, TradeType
from db.db import ConnectionDB

logger = logging.getLogger(__name__)

WalletData = namedtuple('WalletData', 'qty pru currency',
                        defaults=(Decimal('0.0'), Decimal('0.0'), None))

PnlData = namedtuple('PnlData', 'date asset value currency')

SQL_READ_WALLET="select id, name, description from wallet where id = ?"
SQL_FIND_WALLET="select id, name, description from wallet"
SQL_INSERT_WALLET="insert into wallet(name, description) values(?, ?)"
SQL_UPDATE_WALLET="update wallet set name = ?, description = ? where id = ?"

@dataclass
class PnlTotal:
    asset: str
    value: Decimal
    currency: str


class Wallet:

    def __init__(self, id: Union[int, None], name: str, description: str = None, trades: list[Trade] = None, assets: dict[str, WalletData] = None,
                 pnl: list[PnlData] = None, total_pnl: list[PnlTotal] = None):
        self.id: int = id
        self.name: str = name
        self.description: str = description
        self.trades: list[Trade] = trades
        self.assets: dict[str, WalletData] = assets
        self.pnl: list[PnlData] = pnl
        self.total_pnl: list[PnlTotal] = total_pnl

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, val: int):
        if val is not None and type(val) is not int:
            raise ValueError("L'identifiant doit être un entier.")
        self._id = val

    @property
    def trades(self) -> list[Trade]:
        return self._trades

    @trades.setter
    def trades(self, trades: list[Trade]):
        self._trades = trades

    @property
    def assets(self) -> dict[str, WalletData]:
        return self._assets

    @assets.setter
    def assets(self, assets: dict[str, WalletData]):
        self._assets = assets

    @property
    def pnl(self) -> list[PnlData]:
        return self._pnl

    @pnl.setter
    def pnl(self, pnl: list[PnlData]):
        self._pnl = pnl

    @property
    def pnl_total(self) -> list[PnlTotal]:
        return self._pnl_total

    @pnl_total.setter
    def pnl_total(self, pnl_total: list[PnlTotal]):
        self._pnl_total = pnl_total

    @staticmethod
    def _import_trades(trades: list[Trade]) -> tuple[dict[str, WalletData], list[PnlData], list[PnlTotal]]:
        logger.debug('Entry import_trades')
        asset_wallet = {}
        pnl_data_list = []
        pnl_total_list = []

        if len(trades) > 0:
            for trade in trades:
                logger.debug(f"Trade : {trade}")
                asset1, asset2 = trade.get_assets()
                fee_asset = trade.fee_asset

                # init structures
                if asset1 not in asset_wallet:
                    asset_wallet[asset1] = WalletData()
                if asset2 not in asset_wallet:
                    asset_wallet[asset2] = WalletData()
                if fee_asset not in asset_wallet:
                    asset_wallet[fee_asset] = WalletData()

                logger.debug(f"asset1 : {asset1} - asset2 : {asset2} - fee_asset : {fee_asset}")

                # BUY
                if trade.type == TradeType.BUY:
                    qty = asset_wallet[asset1].qty + trade.qty
                    pru = (((asset_wallet[asset1].qty * asset_wallet[
                        asset1].pru) + trade.total) / qty) if qty != 0.0 else Decimal('0.0')
                    asset_wallet[asset1] = WalletData(qty,
                                                      pru,
                                                      asset2)
                    asset_wallet[asset2] = WalletData(asset_wallet[asset2].qty - trade.total,
                                                      asset_wallet[asset2].pru,
                                                      asset_wallet[asset2].currency)
                    logger.debug('BUY')
                    logger.debug(f"qty : {qty}")
                    logger.debug(f"pru : {pru}")
                    logger.debug(f"asset_wallet[{asset1}] : {asset_wallet[asset1]}")
                    logger.debug(f"asset_wallet[{asset2}] : {asset_wallet[asset2]}")
                # SELL
                elif trade.type == TradeType.SELL:
                    qty = asset_wallet[asset1].qty - trade.qty
                    pnl = trade.total - (trade.qty * asset_wallet[asset1].pru)
                    pnl_data_list.append(PnlData(trade.date, asset1, pnl, asset2))
                    pnl_total_item = [e for e in pnl_total_list if e.asset == asset1 and e.currency == asset2]
                    if pnl_total_item:
                        pnl_total = pnl_total_item[0].value + pnl
                        pnl_total_list[0].value = pnl_total
                    else:
                        pnl_total = pnl
                        pnl_total_list.append(PnlTotal(asset1, pnl_total, asset2))
                    asset_wallet[asset1] = WalletData(qty,
                                                      asset_wallet[asset1].pru if qty != 0 else Decimal('0.0'),
                                                      asset2)
                    asset_wallet[asset2] = WalletData(asset_wallet[asset2].qty + trade.total,
                                                      asset_wallet[asset2].pru,
                                                      asset_wallet[asset2].currency)

                    logger.debug('SELL')
                    logger.debug(f"qty : {qty}")
                    logger.debug(f"pnl : {pnl}")
                    logger.debug(f"pnl_total : {pnl_total}")
                    logger.debug(f"asset_wallet[{asset1}] : {asset_wallet[asset1]}")
                    logger.debug(f"asset_wallet[{asset2}] : {asset_wallet[asset2]}")
                # fees
                asset_wallet[fee_asset] = WalletData(asset_wallet[fee_asset].qty - trade.fee,
                                                     asset_wallet[fee_asset].pru,
                                                     asset_wallet[fee_asset].currency)
                logger.debug(f"asset_wallet[{fee_asset}] : {asset_wallet[fee_asset]}")

        return asset_wallet, sorted(pnl_data_list, key=lambda e: e.date), pnl_total_list

    def _merge(self, asset_wallet: dict[str, WalletData], pnl_data_list: list[PnlData], pnl_total_list: list[PnlTotal]):
        pass
        # load data from db
        # if self.assets is None:

    # merge

    def import_trades_from_csv_file(self, filename: str):
        csv_trades = Trade.get_trades_from_csv_file(filename)
        new_trades = Trade.filter_new_trades(csv_trades)
        assets, pnl, pnl_total = Wallet._import_trades(new_trades)
        self._merge(assets, pnl, pnl_total)

        return assets, pnl, pnl_total

    def _is_creation(self) -> bool:
        return self.id is None

    def _validate(self):
        if not self.name:
            raise EntityValidateError("Le nom du wallet est obligatoire")

    @staticmethod
    def read(id: int) -> 'Wallet':
        ConnectionDB.get_cursor().execute(SQL_READ_WALLET, (id,))
        row = ConnectionDB.get_cursor().fetchone()
        if row is None:
            raise EntityNotFoundError(f"Le portefeuille {id} n'existe pas")
        return Wallet(*row)

    @staticmethod
    def find() -> list['Wallet']:
        ConnectionDB.get_cursor().execute(SQL_FIND_WALLET)
        rows = ConnectionDB.get_cursor().fetchall()
        return [Wallet(*row) for row in rows]

    def save(self):
        global cur
        self._validate()
        if self._is_creation():
            cur = ConnectionDB.get_cursor().execute(SQL_INSERT_WALLET, (self.name, self.description))
            self.id = cur.lastrowid
        else:
            cur = ConnectionDB.get_cursor().execute(SQL_UPDATE_WALLET, (self.name, self.description, self.id))
