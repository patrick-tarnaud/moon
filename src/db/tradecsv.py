import csv
from datetime import datetime

from model.trade import Trade, TradeOrigin, TradeType

# indexes in CSV file from Binance
BINANCE_CSV_INDEX_DATE = 0
BINANCE_CSV_INDEX_PAIR = 1
BINANCE_CSV_INDEX_TRADE_TYPE = 2
BINANCE_CSV_INDEX_PRICE = 3
BINANCE_CSV_INDEX_QTY = 4
BINANCE_CSV_INDEX_TOTAl = 5
BINANCE_CSV_INDEX_FEE = 6
BINANCE_CSV_INDEX_FEE_ASSET = 7


def get_trades_from_csv_file(filename: str) -> list[Trade]:
    """ Import trades from csv file with ';' delimiter

        :param filename: filename of the csv file with path (ie /home/patrick/Documents/Finances/binance-export-trades.csv)
        :returns: a list of Trades
    """
    # loop on csv row and create a trade object for each and add it to the trades list
    trades = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            trades.append(Trade(None, row[BINANCE_CSV_INDEX_PAIR],
                                TradeType.BUY if row[BINANCE_CSV_INDEX_TRADE_TYPE] == 'BUY' else TradeType.SELL,
                                float(row[BINANCE_CSV_INDEX_QTY]), float(row[BINANCE_CSV_INDEX_PRICE]),
                                float(row[BINANCE_CSV_INDEX_TOTAl]),
                                datetime.strptime(row[BINANCE_CSV_INDEX_DATE], '%Y-%m-%d %H:%M:%S'),
                                float(row[BINANCE_CSV_INDEX_FEE]), row[BINANCE_CSV_INDEX_FEE_ASSET], None,
                                TradeOrigin.BINANCE))

    return trades
