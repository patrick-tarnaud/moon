from decimal import Decimal
from pprint import pprint
from pydoc import describe
from threading import Timer
from dataclasses import dataclass
from typing import Any

import moon.common.mail as mail
import moon.common.moon_config as moon_config
import moon.common.utils as utils
from binance.client import Client
from moon.model.assets_wallet import AssetWalletData, AssetsWallet
from moon.model.trade import Trade
from moon.model.wallet import Wallet
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


@dataclass
class AssetDataModelUI:
    qty: Decimal
    qty_binance: Decimal
    pru: Decimal
    prt: Decimal
    price: Decimal
    value: Decimal
    pnl: Decimal


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.text = None
        self.setWindowIcon(QIcon("./images/moon.png"))
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle("Moon !")
        self.statusBar().showMessage("Prêt")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.glayout = QGridLayout()
        self.central_widget.setLayout(self.glayout)
        self.binance_client = Client(moon_config.api_key(), moon_config.api_secret())

        # self.init_menu_bar()

        # self.trades_window = TradesWindow(self)
        # self.setCentralWidget(self.trades_window)

        self.show()

        # asset dashboard init from csv
        csv_trades = Trade.get_trades_from_csv_file(TRADES_CSV_FILE)
        self.assets_wallet, pnl, pnl_total = Wallet.import_trades(0, csv_trades)
        acc_balances = self.binance_client.get_account()["balances"]
        Timer(5, self.get_all_tickers).start()

        label_asset = QLabel("Asset")
        label_qty = QLabel("Quantité calculée")
        label_qty_binance = QLabel("Quantité Binance")
        label_pru = QLabel("PRU")
        label_prt = QLabel("PRT")
        font: QFont = label_asset.font()
        font.setPointSize(15)
        font.setBold(True)
        label_asset.setFont(font)
        label_qty.setFont(font)
        label_qty_binance.setFont(font)
        label_pru.setFont(font)
        label_prt.setFont(font)
        self.glayout.addWidget(label_asset, 0, 0)
        self.glayout.addWidget(label_qty, 0, 1)
        self.glayout.addWidget(label_qty_binance, 0, 2)
        self.glayout.addWidget(label_pru, 0, 3)
        self.glayout.addWidget(label_prt, 0, 4)
        line = 1
        for ind, (asset, data) in enumerate(self.assets_wallet.items(), 1):
            self.glayout.addWidget(QLabel(asset), ind, 0)
            self.glayout.addWidget(QLabel(str(round(data.qty, 3))), ind, 1)
            self.glayout.addWidget(
                QLabel(str(round(Decimal(list(filter(lambda x: x["asset"] == asset, acc_balances))[0]["free"]), 3)))
            )
            self.glayout.addWidget(QLabel(str(round(data.pru, 2)) + " " + data.currency), ind, 3)
            self.glayout.addWidget(QLabel(str(round(data.pru * data.qty, 2)) + " " + data.currency), ind, 4)
            line += 1
        self.button_send_mail = QPushButton("Mail")
        self.button_send_mail.clicked.connect(self.send_mail)  # type: ignore
        self.glayout.addWidget(self.button_send_mail, line, 0)

    def get_all_tickers(self) -> None:
        rep = self.binance_client.get_all_tickers()
        Timer(5, self.get_all_tickers).start()

    @staticmethod
    def get_qty_binance_for_asset(asset: str, balances: Any) -> Decimal:
        return Decimal([bal for bal in balances if bal["asset"] == asset][0]["free"])

    # @staticmethod
    # def convert_to_AssetModelUI(aw: AssetsWallet, acc_balances: Any, tickers: Any) -> dict[str, AssetDataModelUI]:
    #     res: dict[str, AssetDataModelUI] = {}
    #     for asset, data in aw.items():
    #         res[asset] = AssetDataModelUI(data.qty, 
    #                                       MainWindow.get_qty_binance_for_asset(asset),
    #                                       data.pru,
    #                                       data.qty*data.pru,
                                          
                                          
    #         )

    # qty: Decimal
    # qty_binance: Decimal
    # pru: Decimal
    # prt: Decimal
    # price: Decimal
    # value: Decimal
    # pnl: Decimal

    def send_mail(self) -> None:
        mail.send_mail(
            moon_config.mail_from(),
            moon_config.mail_to(),
            "Moon!",
            utils.convert_assets_wallet_to_html(self.assets_wallet),
            mail.MailType.HTML,
        )

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
