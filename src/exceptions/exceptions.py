class EntityNotFoundError(Exception):
    def __init__(self, msg):
        super().__init__(msg)


class AssetNotFoundError(Exception):
    def __init__(self, msg):
        super().__init__(msg)
