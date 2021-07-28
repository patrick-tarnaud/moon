import logging.config
from collections import namedtuple, defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import *
from typing import Union

from exceptions.exceptions import EntityValidateError, EntityNotFoundError, Error, BusinessError
from model.trade import Trade, TradeType, TradeOrigin
from db.db import ConnectionDB
from model.asset_wallet import AssetWallet

logger = logging.getLogger(__name__)

SQL_READ_WALLET = "select id, name, description from wallet where id = ?"
SQL_FIND_WALLET = "select id, name, description from wallet"
SQL_INSERT_WALLET = "insert into wallet(name, description) values(?, ?)"
SQL_UPDATE_WALLET = "update wallet set name = ?, description = ? where id = ?"
SQL_DELETE_WALLET = 'delete from wallet where id = ?'


@dataclass(frozen=True)
class Pnl:
    date: datetime
    asset: str
    value: Decimal
    currency: str


@dataclass
class PnlTotal:
    asset: str
    value: Decimal
    currency: str


class Wallet:

    def __init__(self, id: Union[int, None], name: str, description: str = '', trades: list[Trade] = None,
                 assets: dict[str, AssetWallet] = None,
                 pnl: list[Pnl] = None, pnl_total: list[PnlTotal] = None):
        self.id: int = id
        self.name: str = name
        self.description: str = description
        self.trades: list[Trade] = trades
        self.assets: dict[str, AssetWallet] = assets
        self.pnl: list[Pnl] = pnl
        self.pnl_total: list[PnlTotal] = pnl_total

    @staticmethod
    def _import_trades(trades: list[Trade]) -> tuple[dict[str, AssetWallet], list[Pnl], list[PnlTotal]]:
        logger.debug('Entry _import_trades')
        asset_wallet: defaultdict[str, AssetWallet] = defaultdict(AssetWallet)
        pnl_list: list[Pnl] = []
        pnl_total_list: list[PnlTotal] = []

        if len(trades) > 0:
            for trade in trades:
                logger.debug(f"Trade : {trade}")
                asset1, asset2 = trade.get_assets()
                fee_asset = trade.fee_asset

                logger.debug(f"asset1 : {asset1} - asset2 : {asset2} - fee_asset : {fee_asset}")

                # BUY
                if trade.type == TradeType.BUY:
                    qty = asset_wallet[asset1].qty + trade.qty
                    pru = (((asset_wallet[asset1].qty * asset_wallet[
                        asset1].pru) + trade.total) / qty) if qty != 0.0 else Decimal('0.0')
                    asset_wallet[asset1] = AssetWallet(qty,
                                                       pru,
                                                       asset2)
                    asset_wallet[asset2] = AssetWallet(asset_wallet[asset2].qty - trade.total,
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
                    pnl_list.append(Pnl(trade.date, asset1, pnl, asset2))
                    pnl_total_item = [e for e in pnl_total_list if e.asset == asset1 and e.currency == asset2]
                    if pnl_total_item:
                        pnl_total = pnl_total_item[0].value + pnl
                        pnl_total_list[0].value = pnl_total
                    else:
                        pnl_total = pnl
                        pnl_total_list.append(PnlTotal(asset1, pnl_total, asset2))
                    asset_wallet[asset1] = AssetWallet(qty,
                                                       asset_wallet[asset1].pru if qty != 0 else Decimal('0.0'),
                                                       asset2)
                    asset_wallet[asset2] = AssetWallet(asset_wallet[asset2].qty + trade.total,
                                                       asset_wallet[asset2].pru,
                                                       asset_wallet[asset2].currency)

                    logger.debug('SELL')
                    logger.debug(f"qty : {qty}")
                    logger.debug(f"pnl : {pnl}")
                    logger.debug(f"pnl_total : {pnl_total}")
                    logger.debug(f"asset_wallet[{asset1}] : {asset_wallet[asset1]}")
                    logger.debug(f"asset_wallet[{asset2}] : {asset_wallet[asset2]}")
                # fees
                asset_wallet[fee_asset] = AssetWallet(asset_wallet[fee_asset].qty - trade.fee,
                                                      asset_wallet[fee_asset].pru,
                                                      asset_wallet[fee_asset].currency)
                logger.debug(f"asset_wallet[{fee_asset}] : {asset_wallet[fee_asset]}")

        return asset_wallet, sorted(pnl_list, key=lambda e: e.date), pnl_total_list

    def _merge(self, asset_wallet: dict[str, AssetWallet], pnl_data_list: list[Pnl], pnl_total_list: list[PnlTotal]):
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

    def validate(self):
        errors = []
        if not self.name or type(self.name) is not str:
            errors.append(Error('name', 'Le nom du wallet doit être une chaîne de caractères et est obligatoire'))
        if self.description is not None and type(self.description) is not str:
            errors.append(Error('description', 'La description du wallet doit être une chaîne de caractères.'))
        if errors:
            raise BusinessError(errors)

    @staticmethod
    def read(id_: int) -> 'Wallet':
        ConnectionDB.get_cursor().execute(SQL_READ_WALLET, (id_,))
        row = ConnectionDB.get_cursor().fetchone()
        if row is None:
            raise EntityNotFoundError(id_)
        return Wallet(*row)

    @staticmethod
    def find() -> list['Wallet']:
        ConnectionDB.get_cursor().execute(SQL_FIND_WALLET)
        rows = ConnectionDB.get_cursor().fetchall()
        return [Wallet(*row) for row in rows]

    def save(self) -> None:
        self.validate()
        if self._is_creation():
            cur = ConnectionDB.get_cursor().execute(SQL_INSERT_WALLET, (self.name, self.description))
            self.id = cur.lastrowid
        else:
            ConnectionDB.get_cursor().execute(SQL_UPDATE_WALLET, (self.name, self.description, self.id))

    def delete(self) -> None:
        Wallet.read(self.id)
        ConnectionDB.get_cursor().execute(SQL_DELETE_WALLET, (self.id,))

    def load_trades(self, pair: str = None, trade_type: TradeType = None, begin_date: datetime = None,
                    end_date: datetime = None, origin: TradeOrigin = None) -> list['Trade']:
        self.trades = Trade.find(self.id, *list(locals().values())[1:])
        return self.trades

    def load_pnl(self, begin_date: datetime = None, end_date: datetime = None) -> list[Pnl]:
        pass
