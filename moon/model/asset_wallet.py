from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class AssetWallet:
    qty: Decimal = Decimal('0.0')
    pru: Decimal = Decimal('0.0')
    currency: str = None

    def read(self):
        pass