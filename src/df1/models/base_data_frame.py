# -*- coding: utf-8 -*-

from . import crc16
from .base_frame import BaseFrame
from .tx_symbol import TxSymbol
from ..sts_codes import StsCodes


class BaseDataFrame(BaseFrame):
    def __init__(self, buffer=None):
        if not buffer:
            buffer = [TxSymbol.DLE.value, TxSymbol.STX.value]
            buffer.extend([0x00] * 6)
            buffer.extend([TxSymbol.DLE.value, TxSymbol.ETX.value, 0x00, 0x00])
        super(BaseDataFrame, self).__init__(buffer=buffer)

    def init_with_params(self, cmd, src=0x0, dst=0x0, tns=0x0, data=[]):
        app_layer_data = [dst, src, cmd, StsCodes.SUCCESS.value]
        app_layer_data.extend(self._swap_endian(tns))
        app_layer_data.extend(data)
        self.___set_application_layer_data_and_crc(app_layer_data)

    def ___set_application_layer_data_and_crc(self, app_layer_data):
        crc = crc16.compute_crc(bytearray(app_layer_data))
        self.buffer[-2:] = self._word2byte_list(crc)
        self.buffer[2:-4] = self.__sanitize_application_layer_data(app_layer_data)

    @property
    def sts(self):
        app_layer_data = list(self.__get_unsanitized_application_layer_data())
        sts = app_layer_data[3]
        return StsCodes(sts)

    @property
    def tns(self):
        app_layer_data = list(self.__get_unsanitized_application_layer_data())
        tns_bytes = app_layer_data[4:6]
        return (tns_bytes[0] & 255) + (tns_bytes[1] << 8)

    @tns.setter
    def tns(self, value):
        app_layer_data = list(self.__get_unsanitized_application_layer_data())
        app_layer_data[4:6] = self._swap_endian(value)
        self.___set_application_layer_data_and_crc(app_layer_data)

    def _get_command_data(self):
        app_data = list(self.__get_unsanitized_application_layer_data())
        return app_data[6:]

    def __get_unsanitized_application_layer_data(self):
        last = None
        for b in self.buffer[2:-4]:
            if b != 0x10 or last != 0x10:
                last = b
                yield b
            else:
                last = None

    def is_valid(self):
        app_layer_data = self.__get_unsanitized_application_layer_data()
        crc = crc16.compute_crc(bytearray(app_layer_data))
        expected = self._word2byte_list(crc)
        return expected == self.buffer[-2:]

    def __sanitize_application_layer_data(self, data):
        for b in data:
            yield b
            if b == 0x10:
                yield b

    def _swap_endian(self, word):
        return [word & 255, word >> 8]

    def _word2byte_list(self, word):
        return [word >> 8, word & 255]
