# -*- coding: utf-8 -*-

from . import BaseFrame


class ReplyTimeout(BaseFrame):
    def __init__(self):
        super(ReplyTimeout, self).__init__(buffer=[0x00])
