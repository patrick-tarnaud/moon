import pytest
from model.trade import Trade, TradeType, TradeOrigin
from datetime import datetime


@pytest.fixture
def trade():
    return Trade(1, 'BTCEUR', TradeType.BUY, 100.0, 2.0, 200.0, datetime.fromisoformat('2021-01-01 14:00:00'), 0.5,
                 'EUR', '1', TradeOrigin.BINANCE)


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


def test_set_qty(trade):
    trade.qty = 100
    assert type(trade.qty) is float
    with pytest.raises(ValueError):
        trade.qty = 'a'
    trade.qty = '123'
    assert type(trade.qty) is float
    assert trade.qty == 123


def test_set_price(trade):
    trade.price = 100
    assert type(trade.price) is float
    with pytest.raises(ValueError):
        trade.price = 'a'
    trade.price = '123'
    assert type(trade.price) is float
    assert trade.price == 123


def test_set_total(trade):
    trade.total = 100
    assert type(trade.total) is float
    with pytest.raises(ValueError):
        trade.total = 'a'
    trade.total = '123'
    assert type(trade.total) is float
    assert trade.total == 123


def test_set_date(trade):
    with pytest.raises(ValueError):
        trade.date = 5
    with pytest.raises(ValueError):
        trade.date = datetime.fromisoformat('2021-01-01 88:00:00')
    trade.date = datetime.fromisoformat('2021-01-01 14:00:00')
    assert type(trade.date) is datetime


def test_set_origin(trade):
    trade.origin = 'BINANCE'
    assert type(trade.origin) is TradeOrigin
    with pytest.raises(ValueError):
        trade.origin = 0
    with pytest.raises(ValueError):
        trade.origin = 'bin'


def test_equals(trade):
    other = Trade(1, 'BTCEUR', TradeType.BUY, 100.0, 2.0, 200.0, datetime.fromisoformat('2021-01-01 14:00:00'), 0.5,
                  'EUR', '1', TradeOrigin.BINANCE)
    assert other == trade

def test_not_equals(trade):
    other = Trade(1, 'BTCEUR', TradeType.BUY, 1000.0, 2.0, 200.0, datetime.fromisoformat('2021-01-01 14:00:00'), 0.5,
                  'EUR', '1', TradeOrigin.BINANCE)
    assert other != trade

def test_pair_to_asset():
    assets = Trade.pair_to_asset(['BTCEUR', 'ETHEUR', 'CAKEUSDT', 'HOTBNB'])
    assert type(assets) is set
    assert 'BTC' in assets
    assert 'ETH' in assets
    assert 'CAKE' in assets
    assert 'HOT' in assets
