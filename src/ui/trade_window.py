import datetime

import PySide6.QtCore as QtCore
import dateutils
from PySide6.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QTableWidgetItem, QHBoxLayout, QLineEdit, QLabel, \
    QComboBox, QDateEdit, QGroupBox, QPushButton
from babel.numbers import format_decimal

import utils.utils as utils
from model.trade import Trade, TradeType

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
        # self.show_trades()

    def init_ui(self):
        # search criteria
        self.pair_label = QLabel('Pair :')
        self.pair = QComboBox()
        self.pair.setEditable(True)
        self.pair.addItem('')
        for pair in TradeDB.get_trade_db().get_pairs():
            self.pair.addItem(pair)

        self.type_label = QLabel('Type :')
        self.type = QComboBox()
        self.type.addItem('')
        self.type.addItem('BUY', TradeType.BUY)
        self.type.addItem('SELL', TradeType.SELL)

        self.begin_date_label = QLabel('Date de début')
        self.begin_date = QDateEdit(datetime.date.today() - dateutils.relativedelta(months=3))

        self.end_date_label = QLabel('Date de fin')
        self.end_date = QDateEdit(datetime.date.today())

        self.search_button = QPushButton('&Chercher')
        self.search_button.setDefault(True)
        self.search_button.clicked.connect(self.search_trades)

        # trade tables
        self.trades_table = QTableWidget()
        self.trades_table.setColumnCount(len(TRADE_COL_LABELS))
        self.trades_table.setHorizontalHeaderLabels(TRADE_COL_LABELS)
        self.trades_table.setColumnHidden(0, True)
        self.trades_table.itemClicked.connect(self.item_clicked)
        self.trades_table.cellClicked.connect(self.cell_clicked)

        # layout
        v_layout = QVBoxLayout(self)
        self.setLayout(v_layout)

        criteria_layout = QHBoxLayout(self)
        criteria_group_box = QGroupBox('Critères de recherche  ')
        criteria_group_box.setLayout(criteria_layout)

        criteria_layout.addWidget(self.pair_label)
        criteria_layout.addWidget(self.pair)
        criteria_layout.addWidget(self.type_label)
        criteria_layout.addWidget(self.type)
        criteria_layout.addWidget(self.begin_date_label)
        criteria_layout.addWidget(self.begin_date)
        criteria_layout.addWidget(self.end_date_label)
        criteria_layout.addWidget(self.end_date)
        criteria_layout.addWidget(self.search_button)

        v_layout.addWidget(criteria_group_box)
        v_layout.addWidget(self.trades_table)

    def item_clicked(self, item):
        print('item_clicked')
        print(str(item))

    def cell_clicked(self, row, col):
        print('cell_clicked')
        print(row, col)

    def search_trades(self) -> None:
        trade_db = TradeDB.get_trade_db()
        trades = trade_db.find(self.pair.currentText(), self.type.itemData(self.type.currentIndex()),
                               utils.convert_date_to_datetime(self.begin_date.date().toPython(), "00:00:00"),
                               utils.convert_date_to_datetime(self.end_date.date().toPython(), "23:59:59"))
        self.trades_table.clearContents()
        self.trades_table.setRowCount(len(trades))
        row = 0
        for trade in trades:
            self.add_trade_to_table(row, trade)
            row += 1
        self.trades_table.setSortingEnabled(True)
        self.trades_table.sortByColumn(TRADE_COL_DATE, QtCore.Qt.AscendingOrder)
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

        # date
        item = QTableWidgetItem(str(trade.date))
        item.setFlags(item.flags() & ~QtCore.Qt.ItemIsEditable)
        self.trades_table.setItem(row, TRADE_COL_DATE, item)

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
