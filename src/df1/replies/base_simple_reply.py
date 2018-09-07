# -*- coding: utf-8 -*-

from df1.models.base_frame import BaseFrame
from df1.models.tx_symbol import TxSymbol


class BaseSimpleReply(BaseFrame):
    def __init__(self, tx_symbol):
        super(BaseSimpleReply, self).__init__(buffer=[TxSymbol.DLE.value, tx_symbol.value])
