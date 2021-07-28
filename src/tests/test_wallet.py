import sqlite3
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

import pytest

from exceptions.exceptions import EntityNotFoundError
from model.trade import Trade, TradeType, TradeOrigin
from model.wallet import Wallet
from db.db import ConnectionDB


@pytest.fixture
def setup_db():
    ConnectionDB.set_db(':memory:')
    with open('./src/db/db.sql', 'r') as f:
        ddl = f.read()
        ConnectionDB.get_cursor().executescript(ddl)


# @pytest.fixture()
# def trades():
#     return [
#         Trade(None, 'BTCEUR', TradeType.BUY, Decimal('100'), Decimal('2.5'), Decimal('250'),
#               datetime.strptime('2021-05-03 14:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
#               'EUR', None, TradeOrigin.BINANCE),
#         Trade(None, 'BTCEUR', TradeType.BUY, Decimal('200'), Decimal('3'), Decimal('600'),
#               datetime.strptime('2021-05-04 14:00:00', '%Y-%m-%d %H:%M:%S'),
#               Decimal('0.10'),
#               'EUR', None, TradeOrigin.BINANCE),
#         Trade(None, 'BTCEUR', TradeType.SELL, Decimal('50'), Decimal('4'), Decimal('200'),
#               datetime.strptime('2021-05-05 14:00:00', '%Y-%m-%d %H:%M:%S'),
#               Decimal('0.10'),
#               'EUR', None, TradeOrigin.BINANCE),
#         Trade(None, 'ETHEUR', TradeType.BUY, Decimal('300'), Decimal('1'), Decimal('300'),
#               datetime.strptime('2021-05-06 14:00:00', '%Y-%m-%d %H:%M:%S'),
#               Decimal('0.10'),
#               'EUR', None, TradeOrigin.BINANCE),
#         Trade(None, 'ETHEUR', TradeType.BUY, Decimal('150'), Decimal('1.5'), Decimal('225'),
#               datetime.strptime('2021-05-07 14:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
#               'EUR', None, TradeOrigin.BINANCE),
#         Trade(None, 'ETHEUR', TradeType.SELL, Decimal('100'), Decimal('2'), Decimal('200'),
#               datetime.strptime('2021-05-08 14:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
#               'EUR', None, TradeOrigin.BINANCE),
#         Trade(None, 'BNBEUR', TradeType.BUY, Decimal('300'), Decimal('1'), Decimal('300'),
#               datetime.strptime('2021-08-06 14:00:00', '%Y-%m-%d %H:%M:%S'),
#               Decimal('0.10'),
#               'EUR', None, TradeOrigin.BINANCE),
#         Trade(None, 'BNBEUR', TradeType.SELL, Decimal('100'), Decimal('1.5'), Decimal('150'),
#               datetime.strptime('2021-08-06 15:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
#               'EUR', None, TradeOrigin.BINANCE),
#         Trade(None, 'CAKEBNB', TradeType.BUY, Decimal('5'), Decimal('2'), Decimal('10'),
#               datetime.strptime('2021-08-06 16:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
#               'EUR', None, TradeOrigin.BINANCE)
#     ]
@pytest.fixture
def fill_db(setup_db):
    ConnectionDB.get_cursor().executescript("insert into wallet(name, description) values('wallet1', 'desc1')")
    ConnectionDB.get_cursor().executescript("insert into wallet(name, description) values('wallet2', 'desc2')")
    ConnectionDB.get_cursor().executescript("insert into wallet(name, description) values('wallet3', 'desc3')")
    ConnectionDB.get_cursor().executescript("insert into wallet(name, description) values('wallet4', 'desc4')")
    ConnectionDB.commit()


@pytest.fixture()
def imported_trades():
    return [
        Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('2'), Decimal('1000'), Decimal('2000'),
              datetime.strptime('2020-06-01 14:00:01', '%Y-%m-%d %H:%M:%S'), Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('3'), Decimal('500'), Decimal('1500'),
              datetime.strptime('2020-06-01 14:00:02', '%Y-%m-%d %H:%M:%S'),
              Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BTCEUR', TradeType.SELL, Decimal('2'), Decimal('750'), Decimal('1500'),
              datetime.strptime('2020-06-01 14:00:03', '%Y-%m-%d %H:%M:%S'),
              Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BTCEUR', TradeType.SELL, Decimal('2'), Decimal('800'), Decimal('1600'),
              datetime.strptime('2020-06-01 14:00:04', '%Y-%m-%d %H:%M:%S'),
              Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('10'), Decimal('900'), Decimal('9000'),
              datetime.strptime('2020-06-01 14:00:05', '%Y-%m-%d %H:%M:%S'), Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BTCEUR', TradeType.SELL, Decimal('11'), Decimal('500'), Decimal('5500'),
              datetime.strptime('2020-06-01 14:00:06', '%Y-%m-%d %H:%M:%S'), Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('5'), Decimal('1000'), Decimal('5000'),
              datetime.strptime('2020-06-01 14:00:07', '%Y-%m-%d %H:%M:%S'),
              Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BNBBTC', TradeType.BUY, Decimal('5'), Decimal('0.25'), Decimal('1.25'),
              datetime.strptime('2020-06-01 14:00:08', '%Y-%m-%d %H:%M:%S'), Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BNBBTC', TradeType.BUY, Decimal('5'), Decimal('0.5'), Decimal('2.5'),
              datetime.strptime('2020-06-01 14:00:09', '%Y-%m-%d %H:%M:%S'), Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BNBBTC', TradeType.SELL, Decimal('5'), Decimal('1'), Decimal('5'),
              datetime.strptime('2020-06-01 14:00:10', '%Y-%m-%d %H:%M:%S'), Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
    ]


# @patch.object(Trade, 'get_trades_from_csv_file')
# @patch.object(Trade, 'filter_new_trades')
# def test_import_trades_from_csv_file(mock_filter_new_trades, mock_get_trades_from_csv_file, imported_trades):
#     wallet = Wallet(1, 'Binance')
#     mock_filter_new_trades.return_value = imported_trades
#     mock_get_trades_from_csv_file.return_value = imported_trades
#     assets_dict, pnl_list, pnl_total_list = wallet.import_trades_from_csv_file(
#         '/home/patrick/Dev/moon/src/tests/data/trades.csv')
#
#     # assets dict controls
#     assert len(assets_dict) == 3
#     assert assets_dict['BTC'] is not None
#     assert assets_dict['BNB'] is not None
#     assert assets_dict['EUR'] is not None
#     assert assets_dict['BTC'].qty == 6.25
#     assert assets_dict['BTC'].pru == 1000
#     assert assets_dict['BTC'].currency == 'EUR'
#     assert assets_dict['BNB'].qty == 5
#     assert assets_dict['BNB'].pru == 0.375
#     assert assets_dict['BNB'].currency == 'BTC'
#     assert assets_dict['EUR'].qty == -8900
#
#     # pnl data list controls
#     assert len(pnl_list) == 4
#     assert pnl_list[0].asset == 'BTC'
#     assert pnl_list[0].value == 100
#     assert pnl_list[0].currency == 'EUR'
#
#     assert pnl_list[0].asset == 'BTC'
#     assert pnl_list[0].value == 100
#     assert pnl_list[0].currency == 'EUR'
#     assert pnl_list[1].asset == 'BTC'
#     assert pnl_list[1].value == 200
#     assert pnl_list[1].currency == 'EUR'
#     assert pnl_list[2].asset == 'BTC'
#     assert pnl_list[2].value == -4200
#     assert pnl_list[2].currency == 'EUR'
#     assert pnl_list[3].asset == 'BNB'
#     assert pnl_list[3].value == 3.125
#     assert pnl_list[3].currency == 'BTC'
#
#     # pnl total list controls
#     assert len(pnl_total_list) == 2
#     assert pnl_total_list[0].asset == 'BTC'
#     assert pnl_total_list[0].value == -3900
#     assert pnl_total_list[0].currency == 'EUR'
#     assert pnl_total_list[1].asset == 'BNB'
#     assert pnl_total_list[1].value == 3.125
#     assert pnl_total_list[1].currency == 'BTC'


def test_import_trades(imported_trades):
    wallet = Wallet(1, 'Binance')
    assets_dict, pnl_list, pnl_total_list = wallet._import_trades(imported_trades)

    # assets dict controls
    assert len(assets_dict) == 3
    assert assets_dict['BTC'] is not None
    assert assets_dict['BNB'] is not None
    assert assets_dict['EUR'] is not None
    assert assets_dict['BTC'].qty == 6.25
    assert assets_dict['BTC'].pru == 1000
    assert assets_dict['BTC'].currency == 'EUR'
    assert assets_dict['BNB'].qty == 5
    assert assets_dict['BNB'].pru == 0.375
    assert assets_dict['BNB'].currency == 'BTC'
    assert assets_dict['EUR'].qty == -8900

    # pnl data list controls
    assert len(pnl_list) == 4
    assert pnl_list[0].asset == 'BTC'
    assert pnl_list[0].value == 100
    assert pnl_list[0].currency == 'EUR'

    assert pnl_list[0].asset == 'BTC'
    assert pnl_list[0].value == 100
    assert pnl_list[0].currency == 'EUR'
    assert pnl_list[1].asset == 'BTC'
    assert pnl_list[1].value == 200
    assert pnl_list[1].currency == 'EUR'
    assert pnl_list[2].asset == 'BTC'
    assert pnl_list[2].value == -4200
    assert pnl_list[2].currency == 'EUR'
    assert pnl_list[3].asset == 'BNB'
    assert pnl_list[3].value == 3.125
    assert pnl_list[3].currency == 'BTC'

    # pnl total list controls
    assert len(pnl_total_list) == 2
    assert pnl_total_list[0].asset == 'BTC'
    assert pnl_total_list[0].value == -3900
    assert pnl_total_list[0].currency == 'EUR'
    assert pnl_total_list[1].asset == 'BNB'
    assert pnl_total_list[1].value == 3.125
    assert pnl_total_list[1].currency == 'BTC'


def test_find_empty(setup_db):
    wallets = Wallet.find()
    assert len(wallets) == 0


def test_find(fill_db):
    wallets = Wallet.find()
    assert len(wallets) == 4


def test_read(fill_db):
    wallet = Wallet.read(1)
    assert wallet.id == 1
    assert wallet.name == 'wallet1'
    assert wallet.description == 'desc1'

    wallet = Wallet.read(4)
    assert wallet.id == 4
    assert wallet.name == 'wallet4'
    assert wallet.description == 'desc4'


@patch.object(Wallet, '_is_creation')
@patch.object(Wallet, 'validate')
def test_save_for_creation(validate, _is_creation, setup_db):
    _is_creation.return_value = True
    validate.return_value = True
    wallet = Wallet(None, 'wallet1', 'description wallet1')
    wallet.save()
    assert wallet.id is not None
    new_wallet = Wallet.read(1)
    assert new_wallet.id == 1
    assert new_wallet.name == 'wallet1'
    assert new_wallet.description == 'description wallet1'


@patch.object(Wallet, '_is_creation')
@patch.object(Wallet, 'validate')
def test_save_for_update(validate, _is_creation, fill_db):
    _is_creation.return_value = False
    validate.return_value = True
    wallet = Wallet.read(1)
    wallet.description = 'description changed !'
    wallet.save()
    wallet = Wallet.read(1)
    assert wallet.description == 'description changed !'


def test_delete(fill_db):
    wallet = Wallet.read(1)
    assert Wallet is not None
    wallet.delete()
    with pytest.raises(EntityNotFoundError):
        Wallet.read(1)


def test_delete_not_found(setup_db):
    with pytest.raises(EntityNotFoundError):
        wallet = Wallet.read(999)
