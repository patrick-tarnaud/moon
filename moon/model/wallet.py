import logging.config
import os
import sys
from datetime import datetime
from decimal import *
from typing import Optional

from moon.db.db import ConnectionDB
from moon.exceptions.exceptions import BusinessError, EntityNotFoundError, Error

from moon.model.assets_wallet import AssetsWallet, AssetWalletData
from moon.model.pnl import Pnl
from moon.model.pnl_total import PnlTotal
from moon.model.trade import Trade, TradeOrigin, TradeType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQL_READ_WALLET = "select id, name, description from wallet where id = ?"
SQL_FIND_WALLET = "select id, name, description from wallet order by id"
SQL_INSERT_WALLET = "insert into wallet(name, description) values(?, ?)"
SQL_UPDATE_WALLET = "update wallet set name = ?, description = ? where id = ?"
SQL_DELETE_WALLET = "delete from wallet where id = ?"


class Wallet:
    def __init__(
        self,
        id_: Optional[int],
        name: str,
        description: str = "",
        trades: Optional[list[Trade]] = None,
        assets_wallet: Optional[AssetsWallet] = None,
        pnl: Optional[list[Pnl]] = None,
        pnl_total: Optional[list[PnlTotal]] = None,
    ):
        self.id = id_
        self.name = name
        self.description = description
        self.trades = trades
        self.assets_wallet = assets_wallet
        self.pnl = pnl
        self.pnl_total = pnl_total

    def __repr__(self) -> str:
        return f"Wallet(id={self.id}, name='{self.name}', description='{self.description}', trades={self.trades!r}, assets_wallet={self.assets_wallet!r}, pnl={self.pnl!r}, pnl_total={self.pnl_total!r})"

    @staticmethod
    def import_trades(id_wallet: int, trades: list[Trade]) -> tuple[AssetsWallet, list[Pnl], list[PnlTotal]]:
        logger.debug("Entry _import_trades")
        assets_wallet: AssetsWallet = AssetsWallet(id_wallet)
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
                    qty = assets_wallet[asset1].qty + trade.qty
                    pru = (
                        (((assets_wallet[asset1].qty * assets_wallet[asset1].pru) + trade.total) / qty)
                        if qty != 0.0
                        else Decimal("0.0")
                    )
                    assets_wallet[asset1] = AssetWalletData(None, qty, pru, asset2)
                    assets_wallet[asset2] = AssetWalletData(
                        None,
                        assets_wallet[asset2].qty - trade.total,
                        assets_wallet[asset2].pru,
                        assets_wallet[asset2].currency,
                    )
                    logger.debug("BUY")
                    logger.debug(f"qty : {qty}")
                    logger.debug(f"pru : {pru}")
                    logger.debug(f"assets_wallet[{asset1}] : {assets_wallet[asset1]}")
                    logger.debug(f"assets_wallet[{asset2}] : {assets_wallet[asset2]}")
                # SELL
                elif trade.type == TradeType.SELL:
                    qty = assets_wallet[asset1].qty - trade.qty
                    pnl = trade.total - (trade.qty * assets_wallet[asset1].pru)
                    pnl_list.append(Pnl(None, trade.date, asset1, pnl, asset2))
                    pnl_total_item = [e for e in pnl_total_list if e.asset == asset1 and e.currency == asset2]
                    if pnl_total_item:
                        pnl_total = pnl_total_item[0].value + pnl
                        pnl_total_item[0].value = pnl_total
                    else:
                        pnl_total = pnl
                        pnl_total_list.append(PnlTotal(None, asset1, pnl_total, asset2))
                    assets_wallet[asset1] = AssetWalletData(
                        None,
                        qty,
                        assets_wallet[asset1].pru if qty != 0 else Decimal("0.0"),
                        asset2,
                    )
                    assets_wallet[asset2] = AssetWalletData(
                        None,
                        assets_wallet[asset2].qty + trade.total,
                        assets_wallet[asset2].pru,
                        assets_wallet[asset2].currency,
                    )
                    logger.debug("SELL")
                    logger.debug(f"qty : {qty}")
                    logger.debug(f"pnl : {pnl}")
                    logger.debug(f"pnl_total : {pnl_total}")
                    logger.debug(f"assets_wallet[{asset1}] : {assets_wallet[asset1]}")
                    logger.debug(f"assets_wallet[{asset2}] : {assets_wallet[asset2]}")
                # fees
                assets_wallet[fee_asset] = AssetWalletData(
                    None,
                    assets_wallet[fee_asset].qty - trade.fee,
                    assets_wallet[fee_asset].pru,
                    assets_wallet[fee_asset].currency,
                )
                logger.debug(f"assets_wallet[{fee_asset}] : {assets_wallet[fee_asset]}")

        # suppress asset with qty == 0
        new_assets_wallet = AssetsWallet(
            id_wallet,
            {asset: data for asset, data in assets_wallet.items() if data.qty != 0},
        )
        
        new_assets_wallet = dict(sorted(new_assets_wallet.items(), key= lambda item: item[1].qty*item[1].pru, reverse=True)) # type: ignore

        return (
            new_assets_wallet,
            sorted(pnl_list, key=lambda x: x.date), # type: ignore
            sorted(pnl_total_list, key=lambda x: x.asset),
        )

    def _merge_assets_wallet(self, assets_wallet: AssetsWallet) -> None:
        if self.assets_wallet is None:
            self.assets_wallet = assets_wallet
        else:
            for asset, assets_data in assets_wallet.items():
                # if asset already in wallet then calculate new qty ad pru
                if asset in self.assets_wallet.keys():
                    assert self.assets_wallet[asset].currency == assets_data.currency, (
                        "Il n'est pas possible d'avoir des currency " "différents pour un même asset. "
                    )
                    new_qty = self.assets_wallet[asset].qty + assets_data.qty
                    new_pru = (
                        (self.assets_wallet[asset].qty * self.assets_wallet[asset].pru)
                        + (assets_data.qty * assets_data.pru)
                    ) / new_qty
                    self.assets_wallet[asset].qty = new_qty
                    self.assets_wallet[asset].pru = new_pru
                # else add asset to assets wallet
                else:
                    self.assets_wallet[asset] = assets_data

    @staticmethod
    def _get_existant_asset(pnl_total_list: list[PnlTotal], asset: str, currency: str) -> Optional[PnlTotal]:
        for ind, p in enumerate(pnl_total_list):
            if p.asset == asset and p.currency == currency:
                return p
        return None

    def _merge_pnl_total(self, pnl_total_list: list[PnlTotal]) -> list[PnlTotal]:
        pnl_total_list_wallet = self.load_pnl_total()
        pnl_total_list_to_save = []
        for pnl_total in pnl_total_list:
            p = self._get_existant_asset(pnl_total_list_wallet, pnl_total.asset, pnl_total.currency)
            if p:
                p.value += pnl_total.value
                pnl_total_list_to_save.append(p)
            else:
                pnl_total_list_to_save.append(pnl_total)
        return pnl_total_list_to_save

    def import_trades_from_csv_file(self, filename: str) -> None:
        csv_trades = Trade.get_trades_from_csv_file(filename)
        new_trades = Trade.filter_new_trades(self.id, csv_trades)
        assets_wallet, pnl, pnl_total = Wallet.import_trades(self.id, new_trades)
        self._merge_assets_wallet(assets_wallet)
        self.assets_wallet.save()
        Pnl.save_all(self.id, pnl)
        pnl_total_list_to_save = self._merge_pnl_total(pnl_total)
        PnlTotal.save_all(self.id, pnl_total_list_to_save)

    def _is_creation(self) -> bool:
        return self.id is None

    def validate(self) -> None:
        errors = []
        if not self.name or type(self.name) is not str:
            errors.append(
                Error(
                    "name",
                    "Le nom du wallet doit être une chaîne de caractères et est obligatoire",
                )
            )
        if self.description is not None and type(self.description) is not str:
            errors.append(
                Error(
                    "description",
                    "La description du wallet doit être une chaîne de caractères.",
                )
            )
        if errors:
            raise BusinessError(errors)

    @staticmethod
    def read(id_: int) -> "Wallet":
        ConnectionDB.get_cursor().execute(SQL_READ_WALLET, (id_,))
        row = ConnectionDB.get_cursor().fetchone()
        if row is None:
            raise EntityNotFoundError(id_)
        wallet = Wallet(*row)
        wallet.assets_wallet = AssetsWallet.load(wallet.id)
        return wallet

    @staticmethod
    def find() -> list["Wallet"]:
        ConnectionDB.get_cursor().execute(SQL_FIND_WALLET)
        rows = ConnectionDB.get_cursor().fetchall()
        wallets = []
        for row in rows:
            wallet = Wallet(*row)
            wallet.assets_wallet = AssetsWallet.load(wallet.id)
            wallets.append(wallet)
        return wallets

    def save(self) -> None:
        self.validate()
        if self._is_creation():
            cur = ConnectionDB.get_cursor().execute(SQL_INSERT_WALLET, (self.name, self.description))
            self.id = cur.lastrowid
        else:
            ConnectionDB.get_cursor().execute(SQL_UPDATE_WALLET, (self.name, self.description, self.id))
        if self.assets_wallet:
            self.assets_wallet.save()

    def delete(self) -> None:
        Wallet.read(self.id)  # type: ignore
        ConnectionDB.get_cursor().execute(SQL_DELETE_WALLET, (self.id,))
        if self.assets_wallet:
            self.assets_wallet.delete()

    def load_trades(
        self,
        pair: str = None,
        trade_type: TradeType = None,
        begin_date: datetime = None,
        end_date: datetime = None,
        origin: TradeOrigin = None,
    ) -> list["Trade"]:
        self.trades = Trade.find(self.id, *list(locals().values())[1:])
        return self.trades  # type: ignore

    def load_pnl(
        self,
        asset: str = None,
        begin_date: datetime = None,
        end_date: datetime = None,
        currency: str = None,
    ) -> list[Pnl]:
        self.pnl = Pnl.find(self.id, *list(locals().values())[1:])
        return self.pnl

    def load_pnl_total(self, asset: Optional[str] = None) -> list[PnlTotal]:
        self.pnl_total = PnlTotal.find(self.id, *list(locals().values())[1:])
        return self.pnl_total

    @staticmethod
    def compute_trades_csv_file_and_export(trades_csv_file: str, out_path: str) -> tuple[str, str, str]:
        csv_trades = Trade.get_trades_from_csv_file(trades_csv_file)
        assets_wallet, pnl, pnl_total = Wallet.import_trades(0, csv_trades)

        with open(os.path.join(out_path, "assets_wallet.csv"), "w") as f:
            f.write("asset;qty;pru;investi\n")
            for asset, data in sorted(assets_wallet.items()):
                f.write(f"{asset};{round(data.qty,6)};{round(data.pru,6)};{round(data.qty*data.pru,6)}\n")

        with open(os.path.join(out_path, "pnl.csv"), "w") as f:
            f.write("date;asset;gain/perte;monnaie\n")
            for p in pnl:
                f.write(f"{p.date};{p.asset};{round(p.value,6)};{p.currency}\n")

        with open(os.path.join(out_path, "pnl_total.csv"), "w") as f:
            f.write("asset;gain/perte;monnaie\n")
            for pt in pnl_total:
                f.write(f"{pt.asset};{round(pt.value,6)};{pt.currency}\n")

        return (
            os.path.join(out_path, "assets_wallet.csv"),
            os.path.join(out_path, "pnl.csv"),
            os.path.join(out_path, "pnl_total.csv"),
        )


if __name__ == "__main__":
    # in moon dir in terminal : python ./model/wallet.py /home/patrick/Documents/Finances/Binance-export-trades.csv /home/patrick/Documents/Finances/moon
    # w = Wallet(None, "d")
    Wallet.compute_trades_csv_file_and_export(sys.argv[1], sys.argv[2])
