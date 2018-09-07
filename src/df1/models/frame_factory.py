# -*- coding: utf-8 -*-

from .tx_symbol import TxSymbol
from df1.replies import ReplyAck, ReplyNak, Reply4f, ReplyEnq


def parse(buffer):
    if len(buffer) == 2:
        return _ack_catalog(buffer)
    else:
        return _frame_catalog(buffer)


def _ack_catalog(buffer):
    if buffer == bytearray([TxSymbol.DLE.value, TxSymbol.ACK.value]):
        return ReplyAck()
    elif buffer == bytearray([TxSymbol.DLE.value, TxSymbol.NAK.value]):
        return ReplyNak()
    elif buffer == bytearray([TxSymbol.DLE.value, TxSymbol.ENQ.value]):
        return ReplyEnq()
    else:
        raise NotImplementedError("This two bytes frame is not implemented: %s" % buffer)  # pragma: nocover


def _frame_catalog(buffer):
    frame_catalog = {
        0x4f: lambda b: Reply4f(buffer=b)
    }
    cmd, fcn = buffer[4], buffer[8]
    if cmd in frame_catalog:
        return frame_catalog[cmd](buffer)
    else:
        raise NotImplementedError("Frame not implemented: %s" % buffer)  # pragma: nocover
