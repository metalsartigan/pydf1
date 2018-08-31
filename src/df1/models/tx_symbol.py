# -*- coding: utf-8 -*-

from enum import Enum


class TxSymbol(Enum):
    """ Official doc page 2-6 """
    STX = 0x02
    ETX = 0x03
    ENQ = 0x05
    ACK = 0x06
    DLE = 0x10
    NAK = 0x0f
