from datetime import datetime
from decimal import *
from unittest.mock import patch

import pytest

from db.db import ConnectionDB
from model.trade import Trade, TradeType, TradeOrigin

NB_TRADES = 9
NB_BUY_TRADES = 6
NB_SELL_TRADES = 3
NB_BTCEUR_TRADES = 3
NB_ETHEUR_TRADES = 2
NB_BNB_TRADES = 3
NB_PAIRS = 4

# CSV_FILENAME = 'binance-export-trades.csv'
NB_TRADES_IN_CSV = 7


@pytest.fixture
def trade():
    return Trade(1, 1, 'BTCEUR', TradeType.BUY, Decimal('100.0'), Decimal('2.0'), Decimal('200.0'),
                 datetime.fromisoformat('2021-01-01 14:00:00'), Decimal('0.5'),
                 'EUR', '1', TradeOrigin.BINANCE)


@pytest.fixture()
def trades():
    return [
        Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('100'), Decimal('2.5'), Decimal('250'),
              datetime.strptime('2021-05-03 14:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('200'), Decimal('3'), Decimal('600'),
              datetime.strptime('2021-05-04 14:00:00', '%Y-%m-%d %H:%M:%S'),
              Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BTCEUR', TradeType.SELL, Decimal('50'), Decimal('4'), Decimal('200'),
              datetime.strptime('2021-05-05 14:00:00', '%Y-%m-%d %H:%M:%S'),
              Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'ETHEUR', TradeType.BUY, Decimal('300'), Decimal('1'), Decimal('300'),
              datetime.strptime('2021-05-06 14:00:00', '%Y-%m-%d %H:%M:%S'),
              Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'ETHEUR', TradeType.BUY, Decimal('150'), Decimal('1.5'), Decimal('225'),
              datetime.strptime('2021-05-07 14:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'ETHEUR', TradeType.SELL, Decimal('100'), Decimal('2'), Decimal('200'),
              datetime.strptime('2021-05-08 14:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BNBEUR', TradeType.BUY, Decimal('300'), Decimal('1'), Decimal('300'),
              datetime.strptime('2021-08-06 14:00:00', '%Y-%m-%d %H:%M:%S'),
              Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BNBEUR', TradeType.SELL, Decimal('100'), Decimal('1.5'), Decimal('150'),
              datetime.strptime('2021-08-06 15:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'CAKEBNB', TradeType.BUY, Decimal('500'), Decimal('2'), Decimal('1000'),
              datetime.strptime('2021-08-06 16:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE)
    ]


@pytest.fixture
def setup_db():
    ConnectionDB.set_db(':memory:')
    with open('./src/db/db.sql', 'r') as f:
        ddl = f.read()
        ConnectionDB.get_cursor().executescript(ddl)


@pytest.fixture
def fill_db(setup_db, trades):
    Trade.save_all(trades)


def test_constructor_value(trade):
    assert trade.id == 1
    assert trade.pair == 'BTCEUR'
    assert trade.type == TradeType.BUY
    assert trade.qty == Decimal('100')
    assert trade.price == Decimal('2')
    assert trade.total == Decimal('200')
    assert trade.date == datetime.fromisoformat('2021-01-01 14:00:00')
    assert trade.fee == Decimal('0.5')
    assert trade.fee_asset == 'EUR'
    assert trade.origin_id == '1'
    assert trade.origin == TradeOrigin.BINANCE


def test_constructor_type(trade):
    assert type(trade.id) is int
    assert type(trade.pair) is str
    assert type(trade.type) is TradeType
    assert type(trade.qty) is Decimal
    assert type(trade.price) is Decimal
    assert type(trade.total) is Decimal
    assert type(trade.date) is datetime
    assert type(trade.fee) is Decimal
    assert type(trade.fee_asset) is str
    assert type(trade.origin_id) is str
    assert type(trade.origin) is TradeOrigin


def test_equals(trade):
    other = Trade(1, 1, 'BTCEUR', TradeType.BUY, Decimal('100.0'), Decimal('2.0'), Decimal('200.0'),
                  datetime.fromisoformat('2021-01-01 14:00:00'), Decimal('0.5'),
                  'EUR', '1', TradeOrigin.BINANCE)
    assert other == trade


def test_equals_no_id(trade):
    other = Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('100.0'), Decimal('2.0'), Decimal('200.0'),
                  datetime.fromisoformat('2021-01-01 14:00:00'), Decimal('0.5'),
                  'EUR', '1', TradeOrigin.BINANCE)
    assert other == trade


def test_not_equals(trade):
    other = Trade(1, 1, 'BTCEUR', TradeType.BUY, Decimal('1000.0'), Decimal('2.0'), Decimal('200.0'),
                  datetime.fromisoformat('2021-01-01 14:00:00'), Decimal('0.5'),
                  'EUR', '1', TradeOrigin.BINANCE)
    assert other != trade


def test_get_assets():
    trade = Trade(1, 1, 'BTCEUR', TradeType.BUY, Decimal('1000.0'), Decimal('2.0'), Decimal('200.0'),
                  datetime.fromisoformat('2021-01-01 14:00:00'), Decimal('0.5'),
                  'EUR', '1', TradeOrigin.BINANCE)
    buy_asset, sell_asset = trade.get_assets()
    assert buy_asset == 'BTC'
    assert sell_asset == 'EUR'
    trade = Trade(1, 1, 'BTCSXP', TradeType.BUY, Decimal('1000.0'), Decimal('2.0'), Decimal('200.0'),
                  datetime.fromisoformat('2021-01-01 14:00:00'), Decimal('0.5'),
                  'EUR', '1', TradeOrigin.BINANCE)
    buy_asset, sell_asset = trade.get_assets()
    assert buy_asset == 'BTC'
    assert sell_asset == 'SXP'


@patch.object(Trade, 'find')
def test_filter_new_trades_0_new_trade(mock_find, trades):
    mock_find.return_value = trades
    origin_trades = [
        Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('100'), Decimal('2.5'), Decimal('250'),
              datetime.strptime('2021-05-03 14:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('200'), Decimal('3'), Decimal('600'),
              datetime.strptime('2021-05-04 14:00:00', '%Y-%m-%d %H:%M:%S'),
              Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE)]
    new_trades = Trade.filter_new_trades(1, origin_trades)
    assert len(new_trades) == 0
    assert mock_find.call_count == 1


@patch.object(Trade, 'find')
def test_filter_new_trades_1_new_trade_for_date(mock_find, trades):
    mock_find.return_value = trades
    origin_trades = [
        Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('100'), Decimal('2.5'), Decimal('250'),
              datetime.strptime('2021-05-03 13:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('200'), Decimal('3'), Decimal('600'),
              datetime.strptime('2021-05-04 14:00:00', '%Y-%m-%d %H:%M:%S'),
              Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE)]
    new_trades = Trade.filter_new_trades(1, origin_trades)
    assert len(new_trades) == 1
    assert new_trades[0] == Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('100'), Decimal('2.5'), Decimal('250'),
                                  datetime.strptime('2021-05-03 13:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
                                  'EUR', '', TradeOrigin.BINANCE)
    assert mock_find.call_count == 1


@patch.object(Trade, 'find')
def test_filter_new_trades_1_new_trade_for_qty(mock_find, trades):
    mock_find.return_value = trades
    origin_trades = [
        Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('100'), Decimal('2.5'), Decimal('250'),
              datetime.strptime('2021-05-03 14:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE),
        Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('100'), Decimal('3'), Decimal('600'),
              datetime.strptime('2021-05-04 14:00:00', '%Y-%m-%d %H:%M:%S'),
              Decimal('0.10'),
              'EUR', '', TradeOrigin.BINANCE)]
    new_trades = Trade.filter_new_trades(1, origin_trades)
    assert len(new_trades) == 1
    assert new_trades[0] == Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('100'), Decimal('3'), Decimal('600'),
                                  datetime.strptime('2021-05-04 14:00:00', '%Y-%m-%d %H:%M:%S'),
                                  Decimal('0.10'),
                                  'EUR', '', TradeOrigin.BINANCE)
    assert mock_find.call_count == 1


@patch.object(Trade, 'filter_new_trades')
def test__import_new_trades(mock_filter, setup_db, trades):
    mock_filter.return_value = trades
    Trade.import_trades(1, trades)
    trades_found = Trade.find()
    assert len(trades_found) == len(trades)


def test_find_no_trades(setup_db):
    found_trades = Trade.find()
    assert len(found_trades) == 0


def test_find_all_trades(fill_db):
    found_trades = Trade.find()
    assert len(found_trades) == NB_TRADES


def test_find_trades_by_pair(fill_db):
    found_trades = Trade.find(1, 'BTCEUR')
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
    trades = Trade.find(1, '*BNB*')
    assert len(trades) == NB_BNB_TRADES


def test_delete_existing_trade(fill_db):
    trade = Trade.read(1)
    trade.delete()
    assert len(Trade.find()) == NB_TRADES - 1


def test_read_min(setup_db):
    t = Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('100'), Decimal('2.5'), Decimal('250'),
              datetime.strptime('2021-05-03 14:00:00', '%Y-%m-%d %H:%M:%S'))
    t.save()
    trade = Trade.read(1)
    assert trade == t

    assert trade.id == t.id
    assert trade.id_wallet == t.id_wallet
    assert trade.pair == t.pair
    assert trade.qty == t.qty
    assert trade.price == t.price
    assert trade.total == t.total
    assert trade.total is not None
    assert trade.fee == t.fee
    assert trade.fee == Decimal('0.0')
    assert trade.fee_asset == t.fee_asset
    assert trade.fee_asset == ''
    assert trade.origin_id == t.origin_id
    assert trade.origin_id == ''
    assert trade.origin == t.origin
    assert trade.origin == TradeOrigin.OTHER


def test_read(setup_db):
    t = Trade(None, 1, 'BTCEUR', TradeType.BUY, Decimal('100'), Decimal('2.5'), Decimal('250'),
              datetime.strptime('2021-05-03 14:00:00', '%Y-%m-%d %H:%M:%S'), Decimal('0.0'), 'EUR', '999',
              TradeOrigin.BINANCE)
    t.save()
    trade = Trade.read(1)
    assert trade == t

    assert trade.id == t.id
    assert trade.id_wallet == t.id_wallet
    assert trade.pair == t.pair
    assert trade.qty == t.qty
    assert trade.price == t.price
    assert trade.total == t.total
    assert trade.total is not None
    assert trade.fee == t.fee
    assert trade.fee is not None
    assert trade.fee_asset == t.fee_asset
    assert trade.fee_asset is not None
    assert trade.origin_id == t.origin_id
    assert trade.origin_id is not None
    assert trade.origin == t.origin
    assert trade.origin is not None


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

# def test_get_trades_from_csv_file():
#     trades = Trade.get_trades_from_csv_file(os.path.join(os.getcwd(), 'src', 'tests', 'data', CSV_FILENAME))
#     assert len(trades) == NB_TRADES_IN_CSV
