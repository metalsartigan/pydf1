from . import BaseFrame


class ReplyTimeout(BaseFrame):
    def __init__(self):
        super().__init__(buffer=[0x00])
