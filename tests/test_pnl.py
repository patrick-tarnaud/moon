from datetime import datetime
from decimal import Decimal
from unittest.mock import patch, Mock

import pytest

from moon.db.db import ConnectionDB
from moon.model.pnl import Pnl
from moon.exceptions.exceptions import EntityNotFoundError

@pytest.fixture
def setup_db():
    ConnectionDB.set_db(':memory:')
    with open('./moon/db/db.sql', 'r') as f:
        ddl = f.read()
        ConnectionDB.get_cursor().executescript(ddl)


@pytest.fixture
def fill_db(setup_db):
    sql_insert = "insert into pnl(id, id_wallet, date, asset, value, currency) values(?,?,?,?,?,?)"
    ConnectionDB.get_cursor().execute(sql_insert,
                                      (1, 1, datetime.fromisoformat('2021-02-15T08:00:00'), 'BTC', 12.0, 'EUR'))
    ConnectionDB.get_cursor().execute(sql_insert,
                                      (2, 1, datetime.fromisoformat('2021-02-17T08:00:00'), 'BTC', -4.0, 'EUR'))
    ConnectionDB.get_cursor().execute(sql_insert,
                                      (3, 1, datetime.fromisoformat('2021-02-18T08:00:00'), 'BNB', -8.0, 'EUR'))
    ConnectionDB.get_cursor().execute(sql_insert,
                                      (4, 1, datetime.fromisoformat('2021-02-19T08:00:00'), 'DOGE', 2.0, 'EUR'))
    ConnectionDB.get_cursor().execute(sql_insert,
                                      (5, 2, datetime.fromisoformat('2021-02-20T08:00:00'), 'ADA', 18.0, 'EUR'))


def test_constructor():
    pnl = Pnl(1, datetime.fromisoformat('2021-02-15T08:00:00'), 'BTC', Decimal('12.0'), 'EUR')
    assert pnl.id == 1
    assert pnl.date == datetime.fromisoformat('2021-02-15 08:00:00')
    assert pnl.asset == 'BTC'
    assert pnl.value == Decimal('12.0')
    assert pnl.currency == 'EUR'


def test_find_without_id_wallet(fill_db):
    with pytest.raises(TypeError):
        Pnl.find()


def test_find_by_id_wallet(fill_db):
    pnl_list = Pnl.find(1)
    assert len(pnl_list) == 4
    asset_list = [pnl.asset for pnl in pnl_list]
    assert 'BTC' in asset_list
    assert 'BNB' in asset_list
    assert 'DOGE' in asset_list
    assert 'ADA' not in asset_list


def test_find_by_dates():
    pnl_list = Pnl.find(1, begin_date=datetime.fromisoformat('2021-02-17T08:00:00'),
                        end_date=datetime.fromisoformat('2021-02-19T08:00:00'))
    assert len(pnl_list) == 3
    asset_list = [pnl.asset for pnl in pnl_list]
    assert 'BTC' in asset_list
    assert 'BNB' in asset_list
    assert 'DOGE' in asset_list


def test_read(fill_db):
    pnl = Pnl.read(3)
    assert pnl.asset == 'BNB'


def test_is_creation():
    pnl = Pnl(None, datetime.now(), 'BTC', Decimal('12.0'), 'EUR')
    assert pnl._is_creation() == True
    pnl = Pnl(2, datetime.now(), 'BTC', Decimal('12.0'), 'EUR')
    assert pnl._is_creation() == False


@patch.object(Pnl, '_is_creation')
def test_save_insert(mock_is_creation: Mock):
    mock_is_creation.return_value = True
    pnl = Pnl(None, datetime.fromisoformat('2021-02-17T08:00:00'), 'BTC', Decimal('12.0'), 'EUR')
    pnl.save(1)
    assert pnl.id is not None
    pnl2 = Pnl.read(pnl.id)
    assert pnl2.asset == 'BTC'

@patch.object(Pnl, '_is_creation')
def test_save_update(mock_is_creation: Mock):
    mock_is_creation.return_value = False
    pnl = Pnl(1, datetime.fromisoformat('2021-02-17T08:00:00'), 'BTC', Decimal('12.0'), 'EUR')
    pnl.save(1)
    pnl2 = Pnl.read(pnl.id)
    assert pnl2.asset == 'BTC'

def test_save_all(fill_db):
    pnl_list = [
        Pnl(None, datetime.now(), 'TEST', Decimal('12.0'), 'EUR'),
        Pnl(1, datetime.now(), 'TEST2', Decimal('11.0'), 'EUR'),
    ]
    Pnl.save_all(1, pnl_list)
    assert len(Pnl.find(1, asset='TEST')) == 1
    assert len(Pnl.find(1, asset='TEST2')) == 1

def test_delete(fill_db):
    pnl = Pnl.read(3)
    pnl.delete()
    with pytest.raises(EntityNotFoundError):
        pnl = Pnl.read(3)

