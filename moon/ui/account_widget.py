from dataclasses import dataclass
from decimal import Decimal
from locale import currency
from threading import Timer
from typing import Any

import moon.common.mail as mail
import moon.common.moon_config as moon_config
import moon.common.utils as utils
from binance.client import Client
from moon.model.assets_wallet import AssetsWallet
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget


@dataclass
class AccountWidgetModel:
    qty: Decimal
    qty_binance: Decimal
    pru: Decimal
    currency: str
    prt: Decimal
    price: Decimal
    value: Decimal
    pnl: Decimal

    @staticmethod
    def get_qty_binance_for_asset(asset: str, balances: Any) -> Decimal:
        return Decimal([bal for bal in balances if bal["asset"] == asset][0]["free"])

    @classmethod
    def convert_to_AssetModelUI(cls, aw: AssetsWallet, balances: Any, tickers: Any) -> dict[str, "AccountWidgetModel"]:
        model: dict[str, AccountWidgetModel] = {}
        for asset, data in aw.items():
            prices = [ticker["price"] for ticker in tickers if ticker["symbol"] == asset + data.currency]
            if prices:
                price = Decimal(prices[0])
                model[asset] = AccountWidgetModel(
                    data.qty,
                    cls.get_qty_binance_for_asset(asset, balances),
                    data.pru,
                    data.currency,
                    data.qty * data.pru,
                    price,
                    data.qty * price,
                    data.qty * price - data.qty * data.pru,
                )
        return model


class AccountWidget(QWidget):
    def __init__(self, aw: AssetsWallet) -> None:
        super().__init__()

        self.binance_client = Client(moon_config.api_key(), moon_config.api_secret())
        balances = self.binance_client.get_account()["balances"]
        tickers = self.binance_client.get_all_tickers()
        self.model = AccountWidgetModel.convert_to_AssetModelUI(aw, balances, tickers)

        v_layout = QVBoxLayout()
        g_account_layout = QGridLayout()
        h_button_layout = QHBoxLayout()

        self.setLayout(v_layout)
        v_layout.addLayout(g_account_layout)
        v_layout.addLayout(h_button_layout)

        title_label_asset = QLabel("Asset")
        title_label_qty = QLabel("Quantité calculée")
        title_label_qty_binance = QLabel("Quantité Binance")
        title_label_pru = QLabel("PRU")
        title_label_prt = QLabel("PRT")
        title_label_price = QLabel("Prix")
        title_label_value = QLabel("Valeur")
        title_label_pnl = QLabel("PNL")

        font: QFont = title_label_asset.font()
        font.setPointSize(15)
        font.setBold(True)
        title_label_asset.setFont(font)
        title_label_qty.setFont(font)
        title_label_qty_binance.setFont(font)
        title_label_pru.setFont(font)
        title_label_prt.setFont(font)
        title_label_price.setFont(font)
        title_label_value.setFont(font)
        title_label_pnl.setFont(font)

        # titles
        g_account_layout.addWidget(title_label_asset, 0, 0)
        g_account_layout.addWidget(title_label_qty, 0, 1)
        g_account_layout.addWidget(title_label_qty_binance, 0, 2)
        g_account_layout.addWidget(title_label_pru, 0, 3)
        g_account_layout.addWidget(title_label_prt, 0, 4)
        g_account_layout.addWidget(title_label_price, 0, 5)
        g_account_layout.addWidget(title_label_value, 0, 6)
        g_account_layout.addWidget(title_label_pnl, 0, 7)

        # datas
        line = 1
        for ind, (asset, data) in enumerate(self.model.items(), start=1):
            g_account_layout.addWidget(QLabel(asset), ind, 0)
            g_account_layout.addWidget(QLabel(str(round(data.qty, 3))), ind, 1)
            g_account_layout.addWidget(QLabel(str(round(data.qty_binance, 3))), ind, 2)
            g_account_layout.addWidget(QLabel(str(round(data.pru, 3)) + " " + data.currency), ind, 3)
            g_account_layout.addWidget(QLabel(str(round(data.prt, 3)) + " " + data.currency), ind, 4)
            g_account_layout.addWidget(QLabel(str(round(data.price, 3)) + " " + data.currency), ind, 5)
            g_account_layout.addWidget(QLabel(str(round(data.value, 3)) + " " + data.currency), ind, 6)
            g_account_layout.addWidget(QLabel(str(round(data.pnl, 3)) + " " + data.currency), ind, 7)
            line += 1
        # self.button_send_mail = QPushButton("Mail")
        # self.button_send_mail.clicked.connect(self.send_mail)  # type: ignore
        # glayout.addWidget(self.button_send_mail, line, 0)

    # def get_all_tickers(self) -> None:
    #     rep = self.binance_client.get_all_tickers()
    #     Timer(5, self.get_all_tickers).start()

    # def send_mail(self) -> None:
    #     mail.send_mail(
    #         moon_config.mail_from(),
    #         moon_config.mail_to(),
    #         "Moon!",
    #         utils.convert_assets_wallet_to_html(self.assets_wallet),
    #         mail.MailType.HTML,
    #     )
