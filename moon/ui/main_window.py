from decimal import Decimal
from pprint import pprint
from pydoc import describe
from threading import Timer
from dataclasses import dataclass
from typing import Any

from moon.model.assets_wallet import AssetWalletData, AssetsWallet
from moon.model.trade import Trade
from moon.model.wallet import Wallet
from moon.ui.account_widget import AccountWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QGridLayout,
    QLabel,
    QLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

# from moon.ui.trade_window import TradesWindow

TRADES_CSV_FILE = "/Users/Patrick/Documents locaux/Finances/Binance-export-trades.csv"


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.text = None
        self.setWindowIcon(QIcon("./images/moon.png"))
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle("Moon !")
        self.statusBar().showMessage("Prêt")

        # asset dashboard init from csv
        csv_trades = Trade.get_trades_from_csv_file(TRADES_CSV_FILE)
        self.assets_wallet, pnl, pnl_total = Wallet.import_trades(0, csv_trades)

        self.central_widget = AccountWidget(self.assets_wallet)
        self.setCentralWidget(self.central_widget)

        # self.init_menu_bar()

        # self.trades_window = TradesWindow(self)
        # self.setCentralWidget(self.trades_window)

        self.show()

        # Timer(5, self.get_all_tickers).start()

    def init_menu_bar(self) -> None:
        """
        Init menu bar
        """
        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu("&Fichier")
        action_import = QAction(
            "&Importer",
            self,
            shortcut="Ctrl+I",
            statusTip="Importer un fichier CSV d'ordres (trades)",
            triggered=self.import_csv_file,
        )
        action_exit = QAction(
            "&Quitter",
            self,
            shortcut="Ctrl+Q",
            statusTip="Quitter l'application",
            triggered=self.close,
        )
        menu_file.addAction(action_import)
        menu_file.addAction(action_exit)

    # def closeEvent(self, event: QCloseEvent) -> None:
    #     print("Application close event received")
    #     event.accept()

    def import_csv_file(self) -> None:
        """
        CSV File import
        """
        # import trades from csv file
        # get the new trades from db (suppress doublon)
        # show the trades
        # calculate qty and PRU for wallet
        dialog = QFileDialog(self)
        dialog.setNameFilter("Fichiers CSV (*.csv)")
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_():
            filename = dialog.selectedFiles()
            QApplication.instance().setOverrideCursor(Qt.WaitCursor)
            new_trades = Trade.import_trades_from_csv_file(filename)
            QApplication.instance().restoreOverrideCursor()
            QMessageBox.information(
                self,
                "Import",
                "Importation réussie.\n Le nombre de trades importés est %i." % (len(new_trades)),
            )
            if new_trades:
                wallet = Wallet.import_trades(new_trades)
                self.trades_window.show_trades()
