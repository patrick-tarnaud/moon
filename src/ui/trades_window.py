import PySide6.QtCore as QtCore
from babel.numbers import format_decimal
from PySide6.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QTableWidgetItem

from db.tradedb import TradeDB
from model.trade import Trade

TRADE_COL_LABELS = ['Id', 'Pair', 'Type', 'Quantité', 'Prix', 'Total', 'Date', 'Taxe', 'Taxe devise', 'Id origine',
                    'Origine']
TRADE_COL_ID = 0
TRADE_COL_PAIR = 1
TRADE_COL_TYPE = 2
TRADE_COL_QTY = 3
TRADE_COL_PRICE = 4
TRADE_COL_TOTAL = 5
TRADE_COL_DATE = 6
TRADE_COL_FEE = 7
TRADE_COL_FEE_ASSET = 8
TRADE_COL_FEE_ORIGIN_ID = 9
TRADE_COL_FEE_ORIGIN = 10


class TradesWindow(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()
        self.show_trades()

    def init_ui(self):
        v_layout = QVBoxLayout(self)
        self.setLayout(v_layout)
        # v_layout.setAlignment(qtcore.Qt.Alignment())

        self.trades_table = QTableWidget(10, 8, self)
        self.trades_table.setColumnCount(len(TRADE_COL_LABELS))
        self.trades_table.setHorizontalHeaderLabels(TRADE_COL_LABELS)
        self.trades_table.setColumnHidden(0, True)
        self.trades_table.itemClicked.connect(self.item_clicked)
        self.trades_table.cellClicked.connect(self.cell_clicked)

        v_layout.addWidget(self.trades_table)

    def item_clicked(self, item):
        print('item_clicked')
        print(str(item))

    def cell_clicked(self, row, col):
        print('cell_clicked')
        print(row, col)

    def show_trades(self) -> None:
        tradedb = TradeDB.get_trade_db()
        trades = tradedb.find()
        self.trades_table.setRowCount(len(trades))
        row = 0
        for trade in trades:
            self.add_trade_to_table(row, trade)
            row += 1
        self.trades_table.setSortingEnabled(True)
        self.trades_table.sortByColumn(5, QtCore.Qt.AscendingOrder)
        self.trades_table.resizeColumnsToContents()

    def add_trade_to_table(self, row: int, trade: Trade) -> None:
        # id : not visible
        item = QTableWidgetItem(str(trade.id))
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.trades_table.setItem(row, TRADE_COL_ID, item)

        # pair
        item = QTableWidgetItem(trade.pair)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.trades_table.setItem(row, TRADE_COL_PAIR, item)

        # type
        item = QTableWidgetItem(trade.type.value)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.trades_table.setItem(row, TRADE_COL_TYPE, item)

        # qty
        item = QTableWidgetItem(format_decimal(trade.qty, decimal_quantization=False))
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.trades_table.setItem(row, TRADE_COL_QTY, item)

        # price
        item = QTableWidgetItem(format_decimal(trade.price, decimal_quantization=False))
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.trades_table.setItem(row, TRADE_COL_PRICE, item)

        # total
        item = QTableWidgetItem(format_decimal(trade.total, decimal_quantization=False))
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.trades_table.setItem(row, TRADE_COL_TOTAL, item)

        # fee
        item = QTableWidgetItem(format_decimal(trade.fee, decimal_quantization=False))
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.trades_table.setItem(row, TRADE_COL_FEE, item)

        # fee asset
        item = QTableWidgetItem(trade.fee_asset)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.trades_table.setItem(row, TRADE_COL_FEE_ASSET, item)

        # origin id
        item = QTableWidgetItem(trade.origin_id)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.trades_table.setItem(row, TRADE_COL_FEE_ORIGIN_ID, item)

        # origin
        item = QTableWidgetItem(trade.origin.value)
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.trades_table.setItem(row, TRADE_COL_FEE_ORIGIN, item)

