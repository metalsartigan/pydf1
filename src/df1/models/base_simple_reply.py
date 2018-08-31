# -*- coding: utf-8 -*-

from .base_frame import BaseFrame
from .tx_symbol import TxSymbol


class BaseSimpleReply(BaseFrame):
    def __init__(self, tx_symbol):
        super(BaseSimpleReply, self).__init__(buffer=[TxSymbol.DLE.value, tx_symbol.value])
