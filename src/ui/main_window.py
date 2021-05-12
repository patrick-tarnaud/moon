from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMainWindow, QFileDialog

import db.tradecsv as tradecsv
from db.tradedb import TradeDB


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """
        UI Setup
        """
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Moon !')

        self.init_menu_bar()

        self.show()

    def init_menu_bar(self):
        """
        Init menu bar
        """
        menu_bar = self.menuBar()
        menu_file = menu_bar.addMenu('&Fichier')
        action_import = QAction('&Importer', self, triggered=self.import_csv_file)
        menu_file.addAction(action_import)

    def import_csv_file(self):
        """
        CSV File import
        """
        dialog = QFileDialog(self)
        dialog.setNameFilter("Fichiers CSV (*.csv)")
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_():
            filename = dialog.selectedFiles()
            trades = tradecsv.get_trades_from_csv_file(filename[0])
            TradeDB.get_trade_db().import_new_trades(trades)
