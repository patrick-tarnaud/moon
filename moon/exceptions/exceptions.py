from dataclasses import dataclass
from typing import Union, Optional


class AssetNotFoundError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class EntityValidateError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


@dataclass(frozen=True)
class Error:
    code: str
    label: str


class BusinessError(Exception):
    def __init__(self, errors: Optional[Union[list[Error], Error]] = None):
        if not errors:
            self.errors = []
        elif isinstance(errors, Error):
            self.errors = [errors]
        else:
            self.errors = errors

    def add_error(self, error: Error):
        self.errors.append(error)

    def has_error(self):
        return len(self.errors) > 0


class EntityNotFoundError(BusinessError):
    def __init__(self, id_):
        super().__init__([Error('id', f"L'entité {id_} n'existe pas.")])
