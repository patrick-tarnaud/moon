from binance.client import Client
from pprint import pprint
from datetime import datetime
from model.trade import Trade, TradeOrigin, TradeType
import csv
import os

# api_key and api_secret for Binance API in env
client = Client(os.environ['api_key'], os.environ['api_secret'])

pairs = {'ADAEUR', 'BNBEUR', 'BTCEUR', 'BTTEUR', 'CAKEUSDT', 'CHZEUR', 'DOGEEUR', 'DOTEUR', 'EGLDEUR', 'EOSEUR',
         'ETHEUR', 'FILUSDT', 'HNTUSDT', 'HOTUSDT', 'HOTEUR', 'SOLUSDT', 'SXPEUR', 'UNIEUR', 'XLMEUR', 'XRPEUR'}

# indexes in CSV file from Binance
BINANCE_CSV_INDEX_DATE = 0
BINANCE_CSV_INDEX_PAIR = 1
BINANCE_CSV_INDEX_TRADE_TYPE = 2
BINANCE_CSV_INDEX_PRICE = 3
BINANCE_CSV_INDEX_QTY = 4
BINANCE_CSV_INDEX_TOTAl = 5
BINANCE_CSV_INDEX_FEE = 6
BINANCE_CSV_INDEX_FEE_ASSET = 7


def get_my_assets() -> set:
    """Returns traded assets in the user account
        :returns a set of traded assets
    """
    account_snapshot = client.get_account_snapshot(type='SPOT', limit=30)
    # get the assets from user account snapshot
    assets_list = list(
        map(lambda a: list(map(lambda b: b['asset'], a['data']['balances'])), account_snapshot['snapshotVos']))
    assets_set = set()
    for assets in assets_list:
        assets_set = assets_set.union(assets)
    assets_set.remove('USDT')
    return assets_set


def get_my_trades():
    nb_trades = 0
    for pair in pairs:
        trades_for_pair = client.get_my_trades(symbol=pair)
        buy = 0.0
        sell = 0.0
        for trade in trades_for_pair:
            # trades.append(Trade(trade['']))
            print(f'{pair} - Prix :', trade['price'], 'Qty :', trade['qty'], 'Montant :', trade['quoteQty'],
                  'Achat' if bool(trade['isBuyer']) else 'Vente',
                  datetime.fromtimestamp(trade['time'] / 1000).strftime('%d/%m/%y'))
            if bool(trade['isBuyer']):
                buy += float(trade['quoteQty'])
            else:
                sell += float(trade['quoteQty'])
        print(f'{pair} - BUY : {buy} SELL : {sell} PNL : {sell - buy}')
    print(f'nb_trades={nb_trades}')


def import_trades_from_csv_file(filename: str) -> list[Trade]:
    """ Import trades from csv file with ';' delimiter

        :param filename: filename of the csv file with path (ie /home/patrick/Documents/Finances/Binance-export-trades.csv)
        :returns: a list of Trades
    """
    # loop on csv row and create a trade object for each and add it to the trades list
    trades = []
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            trades.append(Trade(None, row[BINANCE_CSV_INDEX_PAIR],
                          TradeType.BUY if row[BINANCE_CSV_INDEX_TRADE_TYPE] == 'BUY' else TradeType.SELL,
                          float(row[BINANCE_CSV_INDEX_QTY]), float(row[BINANCE_CSV_INDEX_PRICE]), float(row[BINANCE_CSV_INDEX_TOTAl]),
                          datetime.strptime(row[BINANCE_CSV_INDEX_DATE], '%Y-%m-%d %H:%M:%S'),
                          float(row[BINANCE_CSV_INDEX_FEE]), row[BINANCE_CSV_INDEX_FEE_ASSET], None, TradeOrigin.BINANCE))
    return trades


def main():
    # res = get_my_trades()
    # pprint('get_my_trades()', res)
    trades = import_trades_from_csv_file('/home/patrick/Documents/Finances/Binance-export-trades.csv')
    pprint(trades)

if __name__ == '__main__':
    main()
