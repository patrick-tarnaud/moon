from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import QMainWindow, QFileDialog, QApplication, QMessageBox, QWidget, QTextEdit, QVBoxLayout, QGridLayout, QLabel
from moon.model.trade import Trade
from moon.model.wallet import Wallet
from moon.model.assets_wallet import AssetWalletData
# from moon.ui.trade_window import TradesWindow

TRADES_CSF_FILE = "/home/patrick/Documents/Finances/Binance-export-trades.csv"


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
        self.layout = QGridLayout()
        self.central_widget.setLayout(self.layout)

        # self.init_menu_bar()

        # self.trades_window = TradesWindow(self)
        # self.setCentralWidget(self.trades_window)

        self.show()

        # asset dashboard init from csv
        csv_trades = Trade.get_trades_from_csv_file(
            "/home/patrick/Documents/Finances/Binance-export-trades.csv")
        assets_wallet, pnl, pnl_total = Wallet._import_trades(0, csv_trades)

        for ind, (asset, data) in enumerate(assets_wallet.items()):
          self.layout.addWidget(QLabel(asset), ind, 0)
          self.layout.addWidget(QLabel(str(data.qty)), ind, 1)
          self.layout.addWidget(QLabel(str(data.pru)), ind, 2)

        # self.wallet_text = QTextEdit()
        # self.layout.addWidget(self.wallet_text)
        # for k, v in assets_wallet.items():
        #     print(k, v)
            # self.wallet_text = self.wallet_text + str(k) + str(v)

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
                "Importation réussie.\n Le nombre de trades importés est %i." % (
                    len(new_trades)),
            )
            if new_trades:
                wallet = Wallet.import_trades(new_trades)
                self.trades_window.show_trades()
