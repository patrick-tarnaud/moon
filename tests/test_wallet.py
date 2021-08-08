import sqlite3
from datetime import datetime
from decimal import Decimal
from unittest.mock import patch, Mock, MagicMock

import pytest

from exceptions.exceptions import EntityNotFoundError
from model.assets_wallet import AssetsWallet, AssetWalletData
from model.trade import Trade, TradeType, TradeOrigin
from model.wallet import Wallet
from db.db import ConnectionDB


@pytest.fixture
def setup_db():
    ConnectionDB.set_db(':memory:')
    with open('./moon/db/db.sql', 'r') as f:
        ddl = f.read()
        ConnectionDB.get_cursor().executescript(ddl)


@pytest.fixture
def fill_db(setup_db):
    ConnectionDB.get_cursor().executescript("insert into wallet(id, name, description) values(1,'wallet1', 'desc1')")
    ConnectionDB.get_cursor().executescript("insert into wallet(id, name, description) values(2, 'wallet2', 'desc2')")
    ConnectionDB.get_cursor().executescript("insert into wallet(id, name, description) values(3, 'wallet3', 'desc3')")
    ConnectionDB.get_cursor().executescript("insert into wallet(id, name, description) values(4, 'wallet4', 'desc4')")
    ConnectionDB.get_cursor().executescript("insert into asset_wallet(id, id_wallet, asset, qty, pru, "
                                            "currency) values(1, 1, 'BTC', 12.0, 2.0, 'EUR')")
    ConnectionDB.get_cursor().executescript("insert into asset_wallet(id, id_wallet, asset, qty, pru, "
                                            "currency) values(2, 1, 'ADA', 5.0, 2.5, 'EUR')")
    ConnectionDB.get_cursor().executescript("insert into asset_wallet(id, id_wallet, asset, qty, pru, "
                                            "currency) values(3, 2, 'BNB', 70.1, 8.0, 'EUR')")
    ConnectionDB.get_cursor().executescript("insert into asset_wallet(id, id_wallet, asset, qty, pru, "
                                            "currency) values(4, 2, 'DOT', 100.0, 5.0, 'EUR')")
    ConnectionDB.commit()


@pytest.fixture()
def imported_trades():
    return [
        Trade(None, 'BTCEUR', TradeType.BUY, Decimal('2'), Decimal('1000'), Decimal('2000'),
              datetime.strptime('2020-06-01 14:00:01', '%Y-%m-%d %H:%M:%S'), Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 'BTCEUR', TradeType.BUY, Decimal('3'), Decimal('500'), Decimal('1500'),
              datetime.strptime('2020-06-01 14:00:02', '%Y-%m-%d %H:%M:%S'),
              Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 'BTCEUR', TradeType.SELL, Decimal('2'), Decimal('750'), Decimal('1500'),
              datetime.strptime('2020-06-01 14:00:03', '%Y-%m-%d %H:%M:%S'),
              Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 'BTCEUR', TradeType.SELL, Decimal('2'), Decimal('800'), Decimal('1600'),
              datetime.strptime('2020-06-01 14:00:04', '%Y-%m-%d %H:%M:%S'),
              Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 'BTCEUR', TradeType.BUY, Decimal('10'), Decimal('900'), Decimal('9000'),
              datetime.strptime('2020-06-01 14:00:05', '%Y-%m-%d %H:%M:%S'), Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 'BTCEUR', TradeType.SELL, Decimal('11'), Decimal('500'), Decimal('5500'),
              datetime.strptime('2020-06-01 14:00:06', '%Y-%m-%d %H:%M:%S'), Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 'BTCEUR', TradeType.BUY, Decimal('5'), Decimal('1000'), Decimal('5000'),
              datetime.strptime('2020-06-01 14:00:07', '%Y-%m-%d %H:%M:%S'),
              Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 'BNBBTC', TradeType.BUY, Decimal('5'), Decimal('0.25'), Decimal('1.25'),
              datetime.strptime('2020-06-01 14:00:08', '%Y-%m-%d %H:%M:%S'), Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 'BNBBTC', TradeType.BUY, Decimal('5'), Decimal('0.5'), Decimal('2.5'),
              datetime.strptime('2020-06-01 14:00:09', '%Y-%m-%d %H:%M:%S'), Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 'BNBBTC', TradeType.SELL, Decimal('5'), Decimal('1'), Decimal('5'),
              datetime.strptime('2020-06-01 14:00:10', '%Y-%m-%d %H:%M:%S'), Decimal('0'),
              'EUR', '', TradeOrigin.BINANCE),
    ]


def test_import_trades(imported_trades):
    wallet = Wallet(1, 'Binance')
    assets_dict, pnl_list, pnl_total_list = wallet._import_trades(wallet.id, imported_trades)

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


@patch.object(AssetsWallet, 'load')
def test_find_empty(mock_load: Mock, setup_db):
    wallets = Wallet.find()
    assert len(wallets) == 0
    mock_load.assert_not_called()

@patch.object(AssetsWallet, 'load')
def test_find(mock_load: Mock, fill_db):
    wallets = Wallet.find()
    assert len(wallets) == 4
    assert mock_load.call_count == 4


@patch.object(AssetsWallet, 'load')
def test_read(mock_load: Mock, fill_db):
    wallet = Wallet.read(1)
    assert wallet.id == 1
    assert wallet.name == 'wallet1'
    assert wallet.description == 'desc1'
    mock_load.assert_called()

    wallet = Wallet.read(4)
    assert wallet.id == 4
    assert wallet.name == 'wallet4'
    assert wallet.description == 'desc4'
    mock_load.assert_called()

@patch.object(AssetsWallet, 'save')
@patch.object(Wallet, '_is_creation')
@patch.object(Wallet, 'validate')
def test_save_for_creation(validate, _is_creation, mock_save: Mock, setup_db):
    _is_creation.return_value = True
    validate.return_value = True
    wallet = Wallet(None, 'wallet1', 'description wallet1')
    wallet.assets_wallet = AssetsWallet(1)
    wallet.assets_wallet['BTC'] = AssetWalletData()
    wallet.save()
    assert wallet.id is not None
    mock_save.assert_called_once()
    new_wallet = Wallet.read(1)
    assert new_wallet.id == 1
    assert new_wallet.name == 'wallet1'
    assert new_wallet.description == 'description wallet1'

@patch.object(AssetsWallet, 'save')
@patch.object(Wallet, '_is_creation')
@patch.object(Wallet, 'validate')
def test_save_for_creation_without_assets_wallet(validate, _is_creation, mock_save: Mock, setup_db):
    _is_creation.return_value = True
    validate.return_value = True
    wallet = Wallet(None, 'wallet1', 'description wallet1')
    wallet.save()
    assert wallet.id is not None
    mock_save.assert_not_called()
    new_wallet = Wallet.read(1)
    assert new_wallet.id == 1
    assert new_wallet.name == 'wallet1'
    assert new_wallet.description == 'description wallet1'

@patch.object(AssetsWallet, 'save')
@patch.object(Wallet, '_is_creation')
@patch.object(Wallet, 'validate')
def test_save_for_update(validate, _is_creation, mock_save: Mock,fill_db):
    _is_creation.return_value = False
    validate.return_value = True
    wallet = Wallet.read(1)
    wallet.description = 'description changed !'
    wallet.save()
    mock_save.assert_called_once()
    wallet = Wallet.read(1)
    assert wallet.description == 'description changed !'

@patch.object(AssetsWallet, 'delete')
def test_delete(mock_delete: Mock, fill_db):
    wallet = Wallet.read(1)
    assert Wallet is not None
    wallet.delete()
    mock_delete.assert_called_once()
    with pytest.raises(EntityNotFoundError):
        Wallet.read(1)


