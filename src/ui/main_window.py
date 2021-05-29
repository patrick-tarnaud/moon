from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent, QIcon
from PySide6.QtWidgets import QMainWindow, QFileDialog, QApplication, QMessageBox

from model.trade import Trade
from model.wallet import Wallet
from ui.trade_window import TradesWindow


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setWindowIcon(QIcon('./images/moon.png'))

    def init_ui(self):
        """
        UI Setup
        """
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Moon !')
        self.statusBar().showMessage('Prêt')
        self.init_menu_bar()

        self.trades_window = TradesWindow(self)
        self.setCentralWidget(self.trades_window)

        self.show()

    def init_menu_bar(self):
        """
        Init menu bar
        """
        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu('&Fichier')
        action_import = QAction('&Importer', self, shortcut="Ctrl+I",
                                statusTip="Importer un fichier CSV d'ordres (trades)", triggered=self.import_csv_file)
        action_exit = QAction("&Quitter", self, shortcut="Ctrl+Q", statusTip="Quitter l'application",
                              triggered=self.close)
        menu_file.addAction(action_import)
        menu_file.addAction(action_exit)

    def closeEvent(self, event: QCloseEvent) -> None:
        print('Application close event received')
        event.accept()

    def import_csv_file(self):
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
            QMessageBox.information(self, 'Import',
                                    'Importation réussie.\n Le nombre de trades importés est %i.' % (
                                        len(new_trades)))
            if new_trades:
                wallet = Wallet.import_trades(new_trades)
                self.trades_window.show_trades()
