from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QIcon, QFont
from PySide6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QApplication,
    QMessageBox,
    QWidget,
    QTextEdit,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QLayout,
)
from moon.model.trade import Trade
from moon.model.wallet import Wallet
from moon.model.assets_wallet import AssetWalletData

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

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.glayout = QGridLayout()
        self.central_widget.setLayout(self.glayout)

        # self.init_menu_bar()

        # self.trades_window = TradesWindow(self)
        # self.setCentralWidget(self.trades_window)

        self.show()

        # asset dashboard init from csv
        csv_trades = Trade.get_trades_from_csv_file(TRADES_CSV_FILE)
        assets_wallet, pnl, pnl_total = Wallet._import_trades(0, csv_trades)

        label_asset = QLabel("Asset")
        label_qty = QLabel("Quantité")
        label_pru = QLabel("PRU")
        label_prt = QLabel("PRT")
        font: QFont = label_asset.font()
        font.setPointSize(15)
        font.setBold(True)
        label_asset.setFont(font)
        label_qty.setFont(font)
        label_pru.setFont(font)
        label_prt.setFont(font)
        self.glayout.addWidget(label_asset, 0, 0)
        self.glayout.addWidget(label_qty, 0, 1)
        self.glayout.addWidget(label_pru, 0, 2)
        self.glayout.addWidget(label_prt, 0, 3)
        for ind, (asset, data) in enumerate(assets_wallet.items(), 1):
            self.glayout.addWidget(QLabel(asset), ind, 0)
            self.glayout.addWidget(QLabel(str(round(data.qty, 3))), ind, 1)
            self.glayout.addWidget(QLabel(str(round(data.pru, 3))), ind, 2)
            self.glayout.addWidget(QLabel(str(round(data.pru * data.qty, 3))), ind, 3)

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
