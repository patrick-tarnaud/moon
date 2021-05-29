import datetime

from model.trade import Trade


class Wallet:
    def __init__(self, id: int = None, name: str = 'Wallet ' + str(datetime.datetime.now()),
                 date: datetime.datetime = datetime.datetime.now()):
        self.id = id
        self.name = name
        self.date = date
        self.assets = {}
        # self.trade_db = TradeDB.get_trade_db()

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, val: int):
        if type(val) is not int:
            raise ValueError("L'id doit être un entier.")
        self._id = val

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        self._name = val

    @property
    def date(self) -> datetime.datetime:
        return self._date

    @date.setter
    def date(self, val: datetime.datetime):
        if type(val) is not datetime.datetime:
            raise ValueError("La doit être une date valide.")
        self._date = val

    @staticmethod
    def import_trades(trades: list[Trade]) -> 'Wallet':
        wallet = Wallet.get_new_wallet_from_last()
        for trade in trades:
            buy_asset, sell_asset = trade.get_assets()
            if buy_asset in wallet.assets.keys():
                pass
                # search existing trades in db to calculate qty and pru
                # trades_from_db = TradeDB.trade_db.find(f'*{buy_asset}*')
                # asset_data_from_db = [lambda t: AssetData(t.qty, t.price) for trade in trades]
                # all_asset_data = asset_data | asset_data_from_db


