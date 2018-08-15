from . import BaseFrame


class InvalidLengthFrame(BaseFrame):
    def __init__(self, buffer):
        super().__init__(buffer=buffer)
