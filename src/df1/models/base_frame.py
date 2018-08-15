from abc import ABC


class BaseFrame(ABC):
    def __init__(self, buffer=[]):
        self.buffer = list(buffer)

    def get_bytes(self) -> bytes:
        return bytes(self.buffer)
