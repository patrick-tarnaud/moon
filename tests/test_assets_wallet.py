from decimal import Decimal
from unittest.mock import patch

import pytest

from db.db import ConnectionDB
from model.assets_wallet import AssetWalletData, AssetsWallet


@pytest.fixture
def setup_db():
    ConnectionDB.set_db(':memory:')
    with open('./moon/db/db.sql', 'r') as f:
        ddl = f.read()
        ConnectionDB.get_cursor().executescript(ddl)


@pytest.fixture
def fill_db_one(setup_db):
    ConnectionDB.get_cursor().executescript("insert into asset_wallet(id, id_wallet, asset, qty, pru, "
                                            "currency) values(1,1, 'BTC', '2.2', '1.2', 'EUR')")
    ConnectionDB.commit()


@pytest.fixture
def fill_db(setup_db):
    ConnectionDB.get_cursor().executescript("insert into asset_wallet(id, id_wallet, asset, qty, pru, "
                                            "currency) values(1, 1, 'BTC', '2.2', '1.2', 'EUR')")
    ConnectionDB.get_cursor().executescript("insert into asset_wallet(id, id_wallet, asset, qty, pru, "
                                            "currency) values(2, 1, 'ETH', '5', '3', 'EUR')")
    ConnectionDB.get_cursor().executescript("insert into asset_wallet(id, id_wallet, asset, qty, pru, "
                                            "currency) values(3, 2, 'BNB', '10', '4.3', 'EUR')")
    ConnectionDB.commit()

def test_load_none(fill_db):
    aw = AssetsWallet.load(999)
    assert aw is None

def test_load_one(fill_db_one):
    aw = AssetsWallet.load(1)
    assert len(aw) == 1
    assert 'BTC' in aw.get_assets()
    assert type(aw['BTC'].qty) is Decimal
    assert type(aw['BTC'].pru) is Decimal
    assert aw['BTC'].id == 1
    assert aw['BTC'].qty == Decimal('2.2')
    assert aw['BTC'].pru == Decimal('1.2')
    assert aw['BTC'].currency == 'EUR'


def test_load(fill_db):
    aw1 = AssetsWallet.load(1)
    assert len(aw1) == 2
    aw2 = AssetsWallet.load(2)
    assert len(aw2) == 1


def test_insert(fill_db):
    aw = AssetsWallet.load(1)
    new_aw = {}
    new_aw['ADA'] = AssetWalletData(None, Decimal('11.0'), Decimal('2.0'), 'EUR')
    new_aw['DOT'] = AssetWalletData(None, Decimal('5.5'), Decimal('1.9'), 'EUR')
    aw._insert(new_aw)
    aw = AssetsWallet.load(1)
    assert len(aw) == 4
    assert 'ADA' in aw.assets_wallet.keys()
    assert aw.assets_wallet['ADA'].id is not None
    assert aw.assets_wallet['ADA'].qty == Decimal('11.0')
    assert aw.assets_wallet['ADA'].pru == Decimal('2.0')
    assert aw.assets_wallet['ADA'].currency == 'EUR'
    assert 'DOT' in aw.assets_wallet.keys()
    assert aw.assets_wallet['DOT'].id is not None
    assert aw.assets_wallet['DOT'].qty == Decimal('5.5')
    assert aw.assets_wallet['DOT'].pru == Decimal('1.9')
    assert aw.assets_wallet['DOT'].currency == 'EUR'


def test_update(fill_db):
    aw = AssetsWallet.load(1)
    aw._update({'BTC': AssetWalletData(aw['BTC'].id, Decimal('120.0'), Decimal('3.0'), 'EUR')})
    aw = AssetsWallet.load(1)
    assert len(aw.get_assets()) == 2
    assert aw['BTC'].qty == Decimal('120.0')
    assert aw['BTC'].pru == Decimal('3.0')

def test_delete(fill_db):
    aw = AssetsWallet.load(1)
    assert len(aw) == 2
    aw._delete([aw['BTC'].id])
    aw = AssetsWallet.load(1)
    assert len(aw) == 1



@patch.object(AssetsWallet, '_insert')
@patch.object(AssetsWallet, '_update')
@patch.object(AssetsWallet, '_delete')
def test_save_insert(mock_delete, mock_update, mock_insert, fill_db):
    aw = AssetsWallet.load(1)
    aw['ADA'] = AssetWalletData(None, Decimal('1.0'), Decimal('2.0'), 'EUR')
    aw.save()
    mock_insert.assert_called_once()
    mock_update.assert_not_called()
    mock_delete.assert_not_called()


@patch.object(AssetsWallet, '_insert')
@patch.object(AssetsWallet, '_update')
@patch.object(AssetsWallet, '_delete')
def test_save_update(mock_delete, mock_update, mock_insert, fill_db):
    aw = AssetsWallet.load(1)
    aw['BTC'].qty = Decimal('12.0')
    aw.save()
    mock_insert.assert_not_called()
    mock_update.assert_called_once()
    mock_delete.assert_not_called()

@patch.object(AssetsWallet, '_insert')
@patch.object(AssetsWallet, '_update')
@patch.object(AssetsWallet, '_delete')
def test_save_delete(mock_delete, mock_update, mock_insert, fill_db):
    aw = AssetsWallet.load(1)
    del aw['BTC']
    aw.save()
    mock_insert.assert_not_called()
    mock_update.assert_not_called()
    mock_delete.assert_called_once()