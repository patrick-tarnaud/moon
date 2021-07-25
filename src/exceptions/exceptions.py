from dataclasses import dataclass


class EntityNotFoundError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


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
    def __init__(self, errors: list[Error] = None):
        self.errors = errors if errors is not None else []

    def add_error(self, error: Error):
        self.errors.append(error)

    def has_error(self):
        return len(self.errors) > 0
