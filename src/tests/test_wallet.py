from datetime import datetime
from decimal import *
from pprint import pprint

import pytest

from model.trade import Trade, TradeType, TradeOrigin
from model.wallet import Wallet


@pytest.fixture()
def trades():
    return [
        Trade(None, 'BTCEUR', TradeType.BUY, Decimal('100'), Decimal('2.5'), Decimal('250'),
              datetime.strptime('2021-05-03 14:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'BTCEUR', TradeType.BUY, Decimal('200'), Decimal('3'), Decimal('600'),
              datetime.strptime('2021-05-04 14:00:00', '%Y-%m-%d %H:%M:%S'),
              Decimal('0.10'),
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'BTCEUR', TradeType.SELL, Decimal('50'), Decimal('4'), Decimal('200'),
              datetime.strptime('2021-05-05 14:00:00', '%Y-%m-%d %H:%M:%S'),
              Decimal('0.10'),
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'ETHEUR', TradeType.BUY, Decimal('300'), Decimal('1'), Decimal('300'),
              datetime.strptime('2021-05-06 14:00:00', '%Y-%m-%d %H:%M:%S'),
              Decimal('0.10'),
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'ETHEUR', TradeType.BUY, Decimal('150'), Decimal('1.5'), Decimal('225'),
              datetime.strptime('2021-05-07 14:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'ETHEUR', TradeType.SELL, Decimal('100'), Decimal('2'), Decimal('200'),
              datetime.strptime('2021-05-08 14:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'BNBEUR', TradeType.BUY, Decimal('300'), Decimal('1'), Decimal('300'),
              datetime.strptime('2021-08-06 14:00:00', '%Y-%m-%d %H:%M:%S'),
              Decimal('0.10'),
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'BNBEUR', TradeType.SELL, Decimal('100'), Decimal('1.5'), Decimal('150'),
              datetime.strptime('2021-08-06 15:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'CAKEBNB', TradeType.BUY, Decimal('5'), Decimal('2'), Decimal('10'),
              datetime.strptime('2021-08-06 16:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
              'EUR', None, TradeOrigin.BINANCE)
    ]


def test_import_trades_from_csv_file():
    # asset_wallet = Wallet.import_trades_from_csv_file('/home/patrick/Dev/moon/src/tests/data/trades.csv')
    # asset_wallet = Wallet.import_trades_from_csv_file('/home/patrick/Dev/moon/src/tests/data/trades.csv')
    wallet = Wallet(1, 'binance')
    asset_wallet = wallet.import_trades_from_csv_file(
        '/home/patrick/Documents/Finances/Binance-export-trades.csv')

    # print()
    # pprint(asset_wallet)
    # pprint({k: v for k, v in asset_wallet.items() if v.qty != 0.0})
    # for asset, asset_data in sorted(asset_wallet.items()):
    #     if asset_data.qty != 0:
    #         print(asset_data.qty)
