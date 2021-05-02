import datetime
from pprint import pprint
import pytest
import sqlite3

from db.tradedb import TradeDB, SQL_INSERT_TRADE
from model.trade import Trade, TradeType, TradeOrigin
from exceptions.exceptions import EntityNotFoundError


@pytest.fixture
def setupdb():
    conn = sqlite3.connect(':memory:')
    cur = conn.cursor()
    cur.executescript('''CREATE TABLE trade(
           id INTEGER PRIMARY KEY,
           pair TEXT,
           type TEXT,
           qty NUMERIC,
           price NUMERIC,
           total NUMERIC,
           date DATETIME,
           fee NUMERIC,
           fee_asset TEXT,
           origin_id TEXT,
           origin TEXT
        );
        
        CREATE INDEX trade_id_index ON trade (id ASC);''')
    return conn


@pytest.fixture
def filldb(setupdb):
    cur = setupdb.cursor()
    trades = [
        ('BTCEUR', 'BUY', 100, 2.5, 250, datetime.datetime.now(), 0.10, 'EUR', '', 'BINANCE'),
        ('BTCEUR', 'BUY', 200, 3, 600, datetime.datetime.now(), 0.10, 'EUR', '', 'BINANCE'),
        ('BTCEUR', 'SELL', 50, 4, 200, datetime.datetime.now(), 0.10, 'EUR', '', 'BINANCE'),
        ('ETHEUR', 'BUY', 300, 1, 300, datetime.datetime.now(), 0.10, 'EUR', '', 'BINANCE'),
        ('ETHEUR', 'BUY', 150, 1.5, 225, datetime.datetime.now(), 0.10, 'EUR', '', 'BINANCE'),
        ('ETHEUR', 'SELL', 100, 2, 200, datetime.datetime.now(), 0.10, 'EUR', '', 'BINANCE')
    ]
    cur.executemany(SQL_INSERT_TRADE, trades)
    setupdb.commit()
    return setupdb


@pytest.fixture
def tradedb(filldb):
    return TradeDB(filldb)


def test_read_trade(tradedb):
    trade = tradedb.read(2)
    assert trade is not None
    print('\n', trade)


def test_read_non_existing_trade(tradedb):
    with pytest.raises(EntityNotFoundError):
        tradedb.read(999)


def test_save_insert_trade(tradedb):
    trade = Trade(None, 'BTCEUR', TradeType.BUY, 1000, 2, 2000, datetime.datetime.now(), 0.20, 'EUR', None,
                  TradeOrigin.BINANCE)
    trade = tradedb.save(trade)
    print('\n', trade)


def test_save_update_trade(tradedb):
    trade = tradedb.read(1)
    print('\n')
    print(f'read trade: {trade}')
    trade.qty = 200
    trade.price = 10
    trade.total = 2000
    updated_trade = tradedb.save(trade)
    print(f'updated trade: {updated_trade}')
    assert trade == updated_trade
    assert trade is not updated_trade


def test_save_all(tradedb):
    original_len = len(tradedb.find())
    trade1 = Trade(None, 'BTCEUR', TradeType.BUY, 1000, 2, 2000, datetime.datetime.now(), 0.20, 'EUR', None,
                   TradeOrigin.BINANCE)
    trade2 = Trade(None, 'BTCEUR', TradeType.BUY, 100, 2, 2000, datetime.datetime.now(), 0.20, 'EUR', None,
                   TradeOrigin.BINANCE)
    tradedb.save_all([trade1, trade2])
    new_len = len(tradedb.find())
    assert new_len == original_len + 2


def test_find_trades(tradedb):
    trades = tradedb.find()
    assert len(trades) == 6
    print('\n')
    pprint(trades)

def test_delete_existing_trade(tradedb):
    assert len(tradedb.find()) == 6
    tradedb.delete(1)
    assert len(tradedb.find()) == 5

def test_delete_non_existing_trade(tradedb):
    with pytest.raises(EntityNotFoundError):
        tradedb.delete(999)
