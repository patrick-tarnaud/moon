from db.tradecsv import get_trades_from_csv_file
import os
import pprint
import pytest

from model.trade import Trade, TradeType, TradeOrigin

csv_filename = 'binance-export-trades.csv'

def test_import():
    trades = get_trades_from_csv_file(os.path.join(os.getcwd(), 'src', 'tests', 'data',  csv_filename))
    assert len(trades) == 7
