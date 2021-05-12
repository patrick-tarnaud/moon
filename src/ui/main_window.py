from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtWidgets import QMainWindow, QFileDialog, QApplication, QMessageBox

import db.tradecsv as tradecsv
from db.tradedb import TradeDB


class MainWindow(QMainWindow):

    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.init_ui()

    def init_ui(self):
        """
        UI Setup
        """
        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('Moon !')
        self.statusBar().showMessage('Prêt')

        self.init_menu_bar()

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
        dialog = QFileDialog(self)
        dialog.setNameFilter("Fichiers CSV (*.csv)")
        dialog.setFileMode(QFileDialog.ExistingFile)
        if dialog.exec_():
            filename = dialog.selectedFiles()
            self.app.setOverrideCursor(Qt.WaitCursor)
            trades = tradecsv.get_trades_from_csv_file(filename[0])
            saved_trades = TradeDB.get_trade_db().import_new_trades(trades)
            self.app.restoreOverrideCursor()
            QMessageBox.information(self, 'Import',
                                    'Import réussi.\n Le nombre de trades lus est %i. \n Le nombre de trades sauvegardés est %i.' % (
                                    len(trades), len(saved_trades)))
