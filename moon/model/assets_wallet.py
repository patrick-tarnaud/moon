from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, ItemsView, KeysView, ValuesView

from moon.db.db import ConnectionDB

SQL_READ = "select id, asset, qty, pru, currency from asset_wallet where id = ?"
SQL_FIND = "select id, asset, qty, pru, currency description from asset_wallet where " \
           "id_wallet = ?"
SQL_INSERT = "insert into asset_wallet(id_wallet, asset, qty, pru, currency) values(?, ?, ?, ?, ?)"
SQL_UPDATE = "update asset_wallet set id_wallet = ?, asset = ?, qty = ?, pru = ?, currency= ? where id = ?"
SQL_DELETE = "delete from asset_wallet where id = ?"
SQL_DELETE_ASSETS_WALLET = "delete from asset_wallet where id_wallet = ?"

SQL_COL_ID = 0
SQL_COL_ASSET = 1
SQL_COL_QTY = 2
SQL_COL_PRU = 3
SQL_COL_CURRENCY = 4


@dataclass
class AssetWalletData:
    id: Optional[int] = None
    qty: Decimal = Decimal('0.0')
    pru: Decimal = Decimal('0.0')
    currency: str = ''


class AssetsWallet:
    """
    Manage assets of a wallet
    """

    def __init__(self, id_wallet: int, dict_asset: Optional[dict[str,AssetWalletData]] = None):
        """
        AssetsWallet constructor
        :param id_wallet: wallet id
        """
        self.id_wallet = id_wallet
        self.assets_wallet: defaultdict[str, AssetWalletData]
        if dict_asset:
            self.assets_wallet = defaultdict(AssetWalletData, dict_asset)
        else:
            self.assets_wallet = defaultdict(AssetWalletData)

    def __repr__(self):
        # return f"{self.assets_wallet}"
        s = "{"
        for asset, data in self.assets_wallet.items():
            s += "'" + asset + f"': AssetWalletData(id={data.id}, qty={data.qty}, data.pru={data.pru}, currency='{data.currency}'),"
        s = s[:-1] + '}'
        return s

    @staticmethod
    def load(id_wallet: int) -> Optional['AssetsWallet']:
        """
        Load assets for a wallet
        :param id_wallet: wallet id
        :return: the assets wallet loaded
        """
        aw = AssetsWallet(id_wallet)
        cur = ConnectionDB.get_cursor().execute(SQL_FIND, (id_wallet,))
        rows = cur.fetchall()
        aw.assets_wallet = defaultdict(AssetWalletData)
        for row in rows:
            aw.assets_wallet[row[SQL_COL_ASSET]] = AssetWalletData(row[SQL_COL_ID],
                                                                   Decimal(str(row[SQL_COL_QTY])),
                                                                   Decimal(str(row[SQL_COL_PRU])),
                                                                   row[SQL_COL_CURRENCY])
        return None if not aw else aw

    def __getitem__(self, key: str):
        return self.assets_wallet[key]

    def __setitem__(self, key: str, value: 'AssetWalletData'):
        self.assets_wallet[key] = value

    def __len__(self):
        return len(self.assets_wallet)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.assets_wallet == other.assets_wallet

    def items(self) -> ItemsView[str, AssetWalletData]:
        return self.assets_wallet.items()

    def keys(self) -> KeysView[str]:
        return self.assets_wallet.keys()

    def values(self) -> ValuesView[AssetWalletData]:
        return self.assets_wallet.values()

    def __delitem__(self, key):
        del self.assets_wallet[key]

    def get_assets(self) -> list[str]:
        return list(self.assets_wallet.keys())

    def get_assets_data(self) -> list[AssetWalletData]:
        return list(self.assets_wallet.values())

    def save(self):
        """
        Save the assets wallet in db
        """
        # read assets in db
        assets_wallet_db = AssetsWallet.load(self.id_wallet)

        # if db contains no assets waller for the wallet : insert all
        if assets_wallet_db is None :
            self._insert_assets(self.assets_wallet)
        else:
            # db not empty
            # get new assets and insert db in batch mode
            new_asset_keys = set(self.assets_wallet.keys()) - set(assets_wallet_db.assets_wallet.keys())
            new_assets = {k: v for k, v in self.assets_wallet.items() if k in new_asset_keys}
            if new_assets:
                self._insert_assets(new_assets)

            # get updated assets and update db in batch mode
            common_asset = set(self.assets_wallet.keys()).intersection(set(assets_wallet_db.assets_wallet.keys()))
            updated_asset = {}
            for asset in common_asset:
                if self.assets_wallet[asset] != assets_wallet_db[asset]:
                    updated_asset[asset] = self.assets_wallet[asset]
            if updated_asset:
                self._update_assets(updated_asset)

            # get deleted assets and delete db in batch mode
            deleted_asset_keys = set(set(assets_wallet_db.assets_wallet.keys() - self.assets_wallet.keys()))
            deleted_asset_ids = [data.id for asset, data in assets_wallet_db.items() if asset in
                                 deleted_asset_keys]
            if deleted_asset_ids:
                self._delete_assets(deleted_asset_ids)

    def _insert_assets(self, inserted_assets: dict[str, AssetWalletData]):
        inserted_assets_list = [(self.id_wallet, asset, float(data.qty), float(data.pru), data.currency)
                                for asset, data in inserted_assets.items()]
        ConnectionDB.get_cursor().executemany(SQL_INSERT, inserted_assets_list)

    def _update_assets(self, updated_assets: dict[str, AssetWalletData]):
        updated_assets_list = [(self.id_wallet, asset, float(data.qty), float(data.pru), data.currency, data.id) for
                               asset, data in updated_assets.items()]
        ConnectionDB.get_cursor().executemany(SQL_UPDATE, updated_assets_list)

    def _delete_assets(self, deleted_assets: list[int]):
        deleted_assets_list = [(id,) for id in deleted_assets]
        ConnectionDB.get_cursor().executemany(SQL_DELETE, deleted_assets_list)

    def delete(self):
        ConnectionDB.get_cursor().execute(SQL_DELETE_ASSETS_WALLET, (self.id_wallet,))

