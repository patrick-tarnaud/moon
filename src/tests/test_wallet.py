from datetime import datetime

from model.asset_data import AssetData
from model.wallet import Wallet


def test_wallet_creation_ok():
    wallet = Wallet(1, 'myWallet', datetime.strptime('2021-05-12 14:00:00', '%Y-%m-%d %H:%M:%S'))
    assert wallet.id == 1
    assert wallet.name == 'myWallet'
    assert wallet.date == datetime.strptime('2021-05-12 14:00:00', '%Y-%m-%d %H:%M:%S')
    assert len(wallet.assets) == 0



