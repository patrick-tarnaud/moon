import os

from db.tradecsv import get_trades_from_csv_file

csv_filename = 'binance-export-trades.csv'


def test_import():
    trades = get_trades_from_csv_file(os.path.join(os.getcwd(), 'src', 'tests', 'data', csv_filename))
    assert len(trades) == 7
