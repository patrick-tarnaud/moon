import os
import sqlite3
from datetime import datetime
from unittest.mock import patch

import pytest

from model.trade import Trade, TradeType, TradeOrigin

NB_TRADES = 9
NB_BUY_TRADES = 6
NB_SELL_TRADES = 3
NB_BTCEUR_TRADES = 3
NB_ETHEUR_TRADES = 3
NB_BNB_TRADES = 3
NB_PAIRS = 4

CSV_FILENAME = 'binance-export-trades.csv'
NB_TRADES_IN_CSV = 7


@pytest.fixture
def trade():
    return Trade(1, 'BTCEUR', TradeType.BUY, 100.0, 2.0, 200.0, datetime.fromisoformat('2021-01-01 14:00:00'), 0.5,
                 'EUR', '1', TradeOrigin.BINANCE)


@pytest.fixture()
def trades():
    return [
        Trade(None, 'BTCEUR', TradeType.BUY, 100, 2.5, 250,
              datetime.strptime('2021-05-03 14:00:00', '%Y-%m-%d %H:%M:%S'), 0.10,
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'BTCEUR', TradeType.BUY, 200, 3, 600, datetime.strptime('2021-05-04 14:00:00', '%Y-%m-%d %H:%M:%S'),
              0.10,
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'BTCEUR', TradeType.SELL, 50, 4, 200, datetime.strptime('2021-05-05 14:00:00', '%Y-%m-%d %H:%M:%S'),
              0.10,
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'ETHEUR', TradeType.BUY, 300, 1, 300, datetime.strptime('2021-05-06 14:00:00', '%Y-%m-%d %H:%M:%S'),
              0.10,
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'ETHEUR', TradeType.BUY, 150, 1.5, 225,
              datetime.strptime('2021-05-07 14:00:00', '%Y-%m-%d %H:%M:%S'), 0.10,
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'ETHEUR', TradeType.SELL, 100, 2, 200,
              datetime.strptime('2021-05-08 14:00:00', '%Y-%m-%d %H:%M:%S'), 0.10,
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'BNBEUR', TradeType.BUY, 300, 1, 300, datetime.strptime('2021-08-06 14:00:00', '%Y-%m-%d %H:%M:%S'),
              0.10,
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'BNBEUR', TradeType.SELL, 100, 1.5, 150,
              datetime.strptime('2021-08-06 15:00:00', '%Y-%m-%d %H:%M:%S'), 0.10,
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'CAKEBNB', TradeType.BUY, 500, 2, 1000,
              datetime.strptime('2021-08-06 16:00:00', '%Y-%m-%d %H:%M:%S'), 0.10,
              'EUR', None, TradeOrigin.BINANCE)
    ]


@pytest.fixture
def setup_db():
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
    Trade._set_connection(conn)
    return conn


@pytest.fixture()
def fill_db(setup_db, trades):
    Trade.save_all(trades)
    return setup_db


def test_constructor_value(trade):
    assert trade.id == 1
    assert trade.pair == 'BTCEUR'
    assert trade.type == TradeType.BUY
    assert trade.qty == 100
    assert trade.price == 2
    assert trade.total == 200
    assert trade.date == datetime.fromisoformat('2021-01-01 14:00:00')
    assert trade.fee == 0.5
    assert trade.fee_asset == 'EUR'
    assert trade.origin_id == '1'
    assert trade.origin == TradeOrigin.BINANCE


def test_constructor_type(trade):
    assert type(trade.id) is int
    assert type(trade.pair) is str
    assert type(trade.type) is TradeType
    assert type(trade.qty) is float
    assert type(trade.price) is float
    assert type(trade.total) is float
    assert type(trade.date) is datetime
    assert type(trade.fee) is float
    assert type(trade.fee_asset) is str
    assert type(trade.origin_id) is str
    assert type(trade.origin) is TradeOrigin


def test_set_type(trade):
    with pytest.raises(ValueError):
        trade.type = 'a'


def test_set_qty_with_int(trade):
    trade.qty = 100
    assert type(trade.qty) is float
    assert trade.qty == 100.0


def test_set_qty_with_alpha(trade):
    with pytest.raises(ValueError):
        trade.qty = 'a'


def test_set_qty_with_str(trade):
    trade.qty = '123'
    assert type(trade.qty) is float
    assert trade.qty == 123


def test_set_price_with_int(trade):
    trade.price = 100
    assert type(trade.price) is float
    assert trade.price == 100.0


def test_set_price_with_alpha(trade):
    with pytest.raises(ValueError):
        trade.price = 'a'


def test_set_price_with_str(trade):
    trade.price = '123'
    assert type(trade.price) is float
    assert trade.price == 123


def test_set_total_with_int(trade):
    trade.total = 100
    assert type(trade.total) is float
    assert trade.total == 100.0


def test_set_total_with_alpha(trade):
    with pytest.raises(ValueError):
        trade.total = 'a'


def test_set_total_with_str(trade):
    trade.total = '123'
    assert type(trade.total) is float
    assert trade.total == 123


def test_total_calculated_value():
    trade = Trade(1, 'BTCEUR', TradeType.BUY, 100.0, 2.0)
    assert trade.total == 200.0


def test_set_date_ok(trade):
    trade.date = datetime.fromisoformat('2021-01-01 14:00:00')
    assert type(trade.date) is datetime


def test_set_date_ko(trade):
    with pytest.raises(ValueError):
        trade.date = 5
    with pytest.raises(ValueError):
        trade.date = datetime.fromisoformat('2021-01-01 88:00:00')


def test_set_origin_ok(trade):
    trade.origin = 'BINANCE'
    assert type(trade.origin) is TradeOrigin
    assert trade.origin == TradeOrigin.BINANCE


def test_set_origin_ko(trade):
    with pytest.raises(ValueError):
        trade.origin = 0
    with pytest.raises(ValueError):
        trade.origin = 'bin'


def test_equals(trade):
    other = Trade(1, 'BTCEUR', TradeType.BUY, 100.0, 2.0, 200.0, datetime.fromisoformat('2021-01-01 14:00:00'), 0.5,
                  'EUR', '1', TradeOrigin.BINANCE)
    assert other == trade


def test_equals_no_id(trade):
    other = Trade(None, 'BTCEUR', TradeType.BUY, 100.0, 2.0, 200.0, datetime.fromisoformat('2021-01-01 14:00:00'), 0.5,
                  'EUR', '1', TradeOrigin.BINANCE)
    assert other == trade


def test_not_equals(trade):
    other = Trade(1, 'BTCEUR', TradeType.BUY, 1000.0, 2.0, 200.0, datetime.fromisoformat('2021-01-01 14:00:00'), 0.5,
                  'EUR', '1', TradeOrigin.BINANCE)
    assert other != trade


def test_get_assets():
    trade = Trade(1, 'BTCEUR', TradeType.BUY, 1000.0, 2.0, 200.0, datetime.fromisoformat('2021-01-01 14:00:00'), 0.5,
                  'EUR', '1', TradeOrigin.BINANCE)
    buy_asset, sell_asset = trade.get_assets()
    assert buy_asset == 'BTC'
    assert sell_asset == 'EUR'
    trade = Trade(1, 'BTCSXP', TradeType.BUY, 1000.0, 2.0, 200.0, datetime.fromisoformat('2021-01-01 14:00:00'), 0.5,
                  'EUR', '1', TradeOrigin.BINANCE)
    buy_asset, sell_asset = trade.get_assets()
    assert buy_asset == 'BTC'
    assert sell_asset == 'SXP'


@patch.object(Trade, 'find')
def test__filter_new_trades_0_new_trade(mock_find, trades):
    mock_find.return_value = trades
    origin_trades = [
        Trade(None, 'BTCEUR', TradeType.BUY, 100, 2.5, 250,
              datetime.strptime('2021-05-03 14:00:00', '%Y-%m-%d %H:%M:%S'), 0.10,
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'BTCEUR', TradeType.BUY, 200, 3, 600, datetime.strptime('2021-05-04 14:00:00', '%Y-%m-%d %H:%M:%S'),
              0.10,
              'EUR', None, TradeOrigin.BINANCE)]
    new_trades = Trade._filter_new_trades(origin_trades)
    assert len(new_trades) == 0
    assert mock_find.call_count == 1


@patch.object(Trade, 'find')
def test__filter_new_trades_1_new_trade_for_date(mock_find, trades):
    mock_find.return_value = trades
    origin_trades = [
        Trade(None, 'BTCEUR', TradeType.BUY, 100, 2.5, 250,
              datetime.strptime('2021-05-03 13:00:00', '%Y-%m-%d %H:%M:%S'), 0.10,
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'BTCEUR', TradeType.BUY, 200, 3, 600, datetime.strptime('2021-05-04 14:00:00', '%Y-%m-%d %H:%M:%S'),
              0.10,
              'EUR', None, TradeOrigin.BINANCE)]
    new_trades = Trade._filter_new_trades(origin_trades)
    assert len(new_trades) == 1
    assert new_trades[0] == Trade(None, 'BTCEUR', TradeType.BUY, 100, 2.5, 250,
                                  datetime.strptime('2021-05-03 13:00:00', '%Y-%m-%d %H:%M:%S'), 0.10,
                                  'EUR', None, TradeOrigin.BINANCE)
    assert mock_find.call_count == 1


@patch.object(Trade, 'find')
def test__filter_new_trades_1_new_trade_for_qty(mock_find, trades):
    mock_find.return_value = trades
    origin_trades = [
        Trade(None, 'BTCEUR', TradeType.BUY, 100, 2.5, 250,
              datetime.strptime('2021-05-03 14:00:00', '%Y-%m-%d %H:%M:%S'), 0.10,
              'EUR', None, TradeOrigin.BINANCE),
        Trade(None, 'BTCEUR', TradeType.BUY, 100, 3, 600, datetime.strptime('2021-05-04 14:00:00', '%Y-%m-%d %H:%M:%S'),
              0.10,
              'EUR', None, TradeOrigin.BINANCE)]
    new_trades = Trade._filter_new_trades(origin_trades)
    assert len(new_trades) == 1
    assert new_trades[0] == Trade(None, 'BTCEUR', TradeType.BUY, 100, 3, 600,
                                  datetime.strptime('2021-05-04 14:00:00', '%Y-%m-%d %H:%M:%S'),
                                  0.10,
                                  'EUR', None, TradeOrigin.BINANCE)
    assert mock_find.call_count == 1


@patch.object(Trade, '_filter_new_trades')
def test__import_new_trades(mock_filter, trades, setup_db):
    mock_filter.return_value = trades
    Trade._import_new_trades(trades)
    trades_found = Trade.find()
    assert len(trades_found) == len(trades)


def test_find_no_trades(setup_db):
    found_trades = Trade.find()
    assert len(found_trades) == 0


def test_find_all_trades(fill_db):
    found_trades = Trade.find()
    assert len(found_trades) == NB_TRADES


def test_find_trades_by_pair(fill_db):
    found_trades = Trade.find('BTCEUR')
    assert len(found_trades) == NB_BTCEUR_TRADES


def test_find_buy_trades(fill_db):
    trades = Trade.find(trade_type=TradeType.BUY)
    assert len(trades) == NB_BUY_TRADES


def test_find_sell_trades(fill_db):
    trades = Trade.find(trade_type=TradeType.SELL)
    assert len(trades) == NB_SELL_TRADES


def test_find_trades_by_dates(fill_db):
    trades = Trade.find(begin_date=datetime.strptime('2021-05-05 14:00:00', '%Y-%m-%d %H:%M:%S'),
                        end_date=datetime.strptime('2021-05-07 14:00:00', '%Y-%m-%d %H:%M:%S'))
    assert len(trades) == 3


def test_find_by_origin(fill_db):
    trades = Trade.find(origin=TradeOrigin.BINANCE)
    assert len(trades) == NB_TRADES


def test_find_multi_criterias_trades(fill_db):
    trades = Trade.find(pair='ETHEUR',
                        begin_date=datetime.strptime('2021-05-05 14:00:00', '%Y-%m-%d %H:%M:%S'),
                        end_date=datetime.strptime('2021-05-07 14:00:00', '%Y-%m-%d %H:%M:%S'),
                        origin=TradeOrigin.BINANCE)
    assert len(trades) == 2


def test_find_with_wildcards(fill_db):
    trades = Trade.find('*BNB*')
    assert len(trades) == NB_BNB_TRADES


def test_delete_existing_trade(fill_db):
    trade = Trade.read(1)
    trade.delete()
    assert len(Trade.find()) == NB_TRADES - 1


def test_read(fill_db):
    trade = Trade.read(1)
    assert trade == Trade(None, 'BTCEUR', TradeType.BUY, 100, 2.5, 250,
                          datetime.strptime('2021-05-03 14:00:00', '%Y-%m-%d %H:%M:%S'), 0.10,
                          'EUR', None, TradeOrigin.BINANCE)


def test_save(setup_db, trades):
    found_trades = Trade.find()
    assert len(found_trades) == 0
    Trade.save(trades.pop())
    found_trades = Trade.find()
    assert len(found_trades) == 1


def test_save_all(setup_db, trades):
    found_trades = Trade.find()
    assert len(found_trades) == 0
    Trade.save_all(trades)
    found_trades = Trade.find()
    assert len(found_trades) == NB_TRADES


def test_get_pairs(fill_db):
    pairs = Trade.get_pairs()
    assert len(pairs) == NB_PAIRS
    assert 'BTCEUR' in pairs
    assert 'ETHEUR' in pairs
    assert 'BNBEUR' in pairs
    assert 'CAKEBNB' in pairs


def test__get_trades_from_csv_file():
    trades = Trade._get_trades_from_csv_file(os.path.join(os.getcwd(), 'src', 'tests', 'data', CSV_FILENAME))
    assert len(trades) == NB_TRADES_IN_CSV
