class AssetData:
    def __init__(self, qty: float = 0.0, price: float = 0.0, total: float = 0.0):
        self.qty = qty
        self.price = price
        self.total = total if total else self.qty * self.price

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val: str):
        if type(val) is not str:
            raise ValueError("Le nom doit être une chaîne de caractères")
        self._name = val

    @property
    def qty(self) -> float:
        return self._qty

    @qty.setter
    def qty(self, val: float):
        if not isinstance(val, (float, int)):
            raise ValueError("La quantité doit être un nombre.")
        self._qty = float(val)
        if hasattr(self, '_price'):
            self.total = self._qty * self._price

    @property
    def price(self) -> float:
        return self._price

    @price.setter
    def price(self, val: float):
        if not isinstance(val, (float, int)):
            raise ValueError("Le prix doit être un nombre.")
        self._price = float(val)
        if hasattr(self, '_qty'):
            self.total = self._qty * self._price

    @property
    def total(self) -> float:
        return self._total

    @total.setter
    def total(self, val: float):
        if not isinstance(val, (float, int)):
            raise ValueError("Le total doit être un nombre.")
        self._total = float(val)

    def __eq__(self, other):
        if not isinstance(other, AssetData):
            return False
        return self.name == other.name and self.qty == other.qty and self.price == other.price and self.total == other.total

    def __hash__(self):
        return hash((self.name, self.qty, self.price, self.total))
