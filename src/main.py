from pprint import pprint

from db.tradecsv import get_trades_from_csv_file
from model.trade import Trade, TradeType

# from binance.client import Client

# api_key and api_secret for Binance API in env
# client = Client(os.environ['api_key'], os.environ['api_secret'])

pairs = {'ADAEUR', 'BNBEUR', 'BTCEUR', 'BTTEUR', 'CAKEUSDT', 'CHZEUR', 'DOGEEUR', 'DOTEUR', 'EGLDEUR', 'EOSEUR',
         'ETHEUR', 'FILUSDT', 'HNTUSDT', 'HOTUSDT', 'HOTEUR', 'SOLUSDT', 'SXPEUR', 'UNIEUR', 'XLMEUR', 'XRPEUR'}


# def get_my_assets() -> set:
#     """Returns traded assets in the user account
#         :returns a set of traded assets
#     """
#     account_snapshot = client.get_account_snapshot(type='SPOT', limit=30)
#     # get the assets from user account snapshot
#     assets_list = list(
#         map(lambda a: list(map(lambda b: b['asset'], a['data']['balances'])), account_snapshot['snapshotVos']))
#     assets_set = set()
#     for assets in assets_list:
#         assets_set = assets_set.union(assets)
#     assets_set.remove('USDT')
#     return assets_set
#
#
# def get_my_trades():
#     nb_trades = 0
#     for pair in pairs:
#         trades_for_pair = client.get_my_trades(symbol=pair)
#         buy = 0.0
#         sell = 0.0
#         for trade in trades_for_pair:
#             # trades.append(Trade(trade['']))
#             print(f'{pair} - Prix :', trade['price'], 'Qty :', trade['qty'], 'Montant :', trade['quoteQty'],
#                   'Achat' if bool(trade['isBuyer']) else 'Vente',
#                   datetime.fromtimestamp(trade['time'] / 1000).strftime('%d/%m/%y'))
#             if bool(trade['isBuyer']):
#                 buy += float(trade['quoteQty'])
#             else:
#                 sell += float(trade['quoteQty'])
#         print(f'{pair} - BUY : {buy} SELL : {sell} PNL : {sell - buy}')
#     print(f'nb_trades={nb_trades}')


def main():
    trades = get_trades_from_csv_file('/home/patrick/Documents/Finances/Binance-export-trades.csv')
    # pprint(trades)
    # print(len(trades))
    # pprint([trade for trade in trades if trade.pair == 'BTCEUR'])

    assets = Trade.pair_to_asset([trade.pair for trade in trades])
    pprint(assets)
    print('BTC',
          sum([trade.qty if trade.type == TradeType.BUY else -trade.qty for trade in trades if trade.pair == 'BTCEUR']))
    print('ETH',
          sum([trade.qty if trade.type == TradeType.BUY else -trade.qty for trade in trades if trade.pair == 'ETHEUR']))
    print('BNB', sum([trade.qty if trade.type == TradeType.BUY else -trade.qty for trade in trades if
                      trade.pair == 'BNBEUR' or trade.pair == 'BNBUSDT']))


if __name__ == '__main__':
    main()
