from PySide6.QtWidgets import QWidget, QTableWidget, QVBoxLayout, QTableWidgetItem

from db.tradedb import TradeDB
from model.trade import TRADE_ATTRIBUTES_LABELS, Trade


class TradesWindow(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.init_ui()
        self.show_trades()

    def init_ui(self):
        v_layout = QVBoxLayout(self)
        self.setLayout(v_layout)

        self.trades_table = QTableWidget(10, 8, self)
        self.trades_table.setColumnCount(len(TRADE_ATTRIBUTES_LABELS))
        self.trades_table.setHorizontalHeaderLabels(TRADE_ATTRIBUTES_LABELS)

        v_layout.addWidget(self.trades_table)

    def show_trades(self) -> None:
        tradedb = TradeDB.get_trade_db()
        trades = tradedb.find()
        self.trades_table.setRowCount(len(trades))
        row = 0
        for trade in trades:
            self.add_trade_to_table(row, trade)
            row += 1

    def add_trade_to_table(self, row: int, trade: Trade) -> None:
        col = 0
        for k in trade.__dict__.keys():
            att = k[1:]
            val = trade.__getattribute__(att)
            # enum cases
            if att == 'type' or att == 'origin':
                val = val.value
            if val is not None:
                item = QTableWidgetItem(str(val))
                self.trades_table.setItem(row, col, item)
            col += 1
