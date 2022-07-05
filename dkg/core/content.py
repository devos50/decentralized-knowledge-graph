class Content:

    def __init__(self, identifier: bytes, data: bytes) -> None:
        self.data: bytes = data
        self.identifier: bytes = identifier
