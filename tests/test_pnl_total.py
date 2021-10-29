from decimal import Decimal
from unittest.mock import patch, Mock

from moon.exceptions.exceptions import EntityNotFoundError
from moon.model.pnl_total import PnlTotal
from moon.db.db import ConnectionDB

import pytest


@pytest.fixture
def setup_db():
    ConnectionDB.set_db(':memory:')
    with open('./moon/db/db.sql', 'r') as f:
        ddl = f.read()
        ConnectionDB.get_cursor().executescript(ddl)


@pytest.fixture
def fill_db(setup_db):
    ConnectionDB.get_cursor().executescript(
        "insert into pnl_total(id_wallet, asset, value, currency) values(1,'BTC',12.0,'EUR')")
    ConnectionDB.get_cursor().executescript(
        "insert into pnl_total(id_wallet, asset, value, currency) values(1,'ADA',3.5,'EUR')")
    ConnectionDB.get_cursor().executescript(
        "insert into pnl_total(id_wallet, asset, value, currency) values(1,'ETH',8.9,'EUR')")
    ConnectionDB.get_cursor().executescript(
        "insert into pnl_total(id_wallet, asset, value, currency) values(2,'BTC',-4,'EUR')")
    ConnectionDB.get_cursor().executescript(
        "insert into pnl_total(id_wallet, asset, value, currency) values(2,'ETH',11,'EUR')")
    ConnectionDB.commit()


def test_constructor_empty():
    with pytest.raises(TypeError):
        p = PnlTotal()


def test_construtor():
    p = PnlTotal(1, 'BTC', Decimal('2.0'), 'EUR')
    assert p.id == 1
    assert p.asset == 'BTC'
    assert p.value == Decimal('2.0')
    assert p.currency == 'EUR'


def test_construtor_with_float_value():
    p = PnlTotal(1, 'BTC', 2.0, 'EUR')
    assert p.id == 1
    assert p.asset == 'BTC'
    assert p.value == Decimal('2.0')
    assert p.currency == 'EUR'


def test_equality():
    p1 = PnlTotal(1, 'BTC', 2.0, 'EUR')
    p2 = PnlTotal(1, 'BTC', 2.0, 'EUR')
    assert p1 == p2

    p1 = PnlTotal(1, 'BTC', 2.0, 'EUR')
    p2 = PnlTotal(2, 'BTC', 2.0, 'EUR')
    assert p1 == p2

    p1 = PnlTotal(1, 'BTC', 2.0, 'EUR')
    p2 = PnlTotal(1, 'BTC', 1.0, 'EUR')
    assert p1 != p2


def test_find_wallet(fill_db):
    l = PnlTotal.find(1)
    assert len(l) == 3

    l = PnlTotal.find(2)
    assert len(l) == 2

    l = PnlTotal.find(999)
    assert len(l) == 0


def test_find_with_asset(fill_db):
    l = PnlTotal.find(1, 'BTC')
    assert len(l) == 1
    p = l[0]
    assert p.asset == 'BTC'
    assert p.value == Decimal('12.0')


def test_read(fill_db):
    p = PnlTotal.read(1)
    assert p is not None
    assert p.asset == 'BTC'
    assert p.value == Decimal('12.0')


def test_read_none(fill_db):
    with pytest.raises(EntityNotFoundError):
        p = PnlTotal.read(999)


def test_delete(fill_db):
    p = PnlTotal.read(1)
    p.delete()
    with pytest.raises(EntityNotFoundError):
        p = PnlTotal.read(1)


def test_is_creation():
    p = PnlTotal(None, 'BTC', 2.0, 'EUR')
    assert p._is_creation()

    p = PnlTotal(1, 'BTC', 2.0, 'EUR')
    assert not p._is_creation()


@patch.object(PnlTotal, '_is_creation')
def test_save_insert(mock_is_creation: Mock, setup_db):
    mock_is_creation.return_value = True
    p = PnlTotal(None, 'BTC', 12.0, 'EUR')
    p.save(1)
    assert p.id is not None
    p = PnlTotal.read(1)
    assert p is not None
    assert p.asset == 'BTC'
    assert p.value == Decimal('12.0')


@patch.object(PnlTotal, '_is_creation')
def test_save_update(mock_is_creation: Mock, fill_db):
    mock_is_creation.return_value = False
    p = PnlTotal.read(1)
    p.asset = 'ADA'
    p.value = Decimal('8.0')
    p.save(1)
    p = PnlTotal.read(1)
    assert p is not None
    assert p.asset == 'ADA'
    assert p.value == Decimal('8.0')

@patch.object(PnlTotal, '_is_creation')
def test_save_all_update(mock__is_creation: Mock,fill_db):
    mock__is_creation.return_value = False
    pnl_total_list = PnlTotal.find(1)
    for pnl_total in pnl_total_list:
        pnl_total.value = Decimal('20.0')
    PnlTotal.save_all(1, pnl_total_list)
    pnl_total_list = PnlTotal.find(1)
    for pnl_total in pnl_total_list:
        assert pnl_total.value == Decimal('20.0')

@patch.object(PnlTotal, '_is_creation')
def test_save_all_insert(mock__is_creation: Mock,setup_db):
    mock__is_creation.return_value = True
    pnl_total_list = []
    for i in range(3):
        pnl_total_list.append(PnlTotal(None, 'BTC', Decimal('20.0') * i, 'EUR'))
    PnlTotal.save_all(1, pnl_total_list)
    pnl_total_list = PnlTotal.find(1)
    assert len(pnl_total_list) == 3
    assert pnl_total_list[0].value == Decimal('0.0')
    assert pnl_total_list[1].value == Decimal('20.0')
    assert pnl_total_list[2].value == Decimal('40.0')

def test_delete_wallet(fill_db):
    pnl_total_list = PnlTotal.find(1)
    assert len(pnl_total_list) == 3
    PnlTotal.delete_wallet(1)
    pnl_total_list = PnlTotal.find(1)
    assert len(pnl_total_list) == 0

