# -*- coding: utf-8 -*-

import socket

from df1.models.base_plc import BasePlc
from df1.models.reply_4f import Reply4f
from df1.models.tx_symbol import TxSymbol


class MockPlc(BasePlc):
    def __init__(self):
        super(MockPlc, self).__init__()
        self.connected = False
        self._init_tables()
        self._last_response = [TxSymbol.DLE.value, TxSymbol.NAK.value]
        self.force_bad_crc_once = False
        self.replies_corrupt_command_once = False
        self._last_message = None
        self.replies_ack_timeout_once = False
        self.sends_corrupt_enq_next = False
        self.message_sink_is_full_for_next_nb_commands = 0
        self.sends_corrupt_ack_once = False
        self.dont_reply_data_frame = False
        self.replies_invalid_length_frame_once = False
        self.replies_timeout = False
        self.replies_nak = False
        self.does_not_reply = False
        self.always_replies_messages = False
        self.replies_segmented = False

    def _init_tables(self):
        self._tables = [
            [0xd8, 0x8, 0x15, 0xe5, 0x99, 0xab, 0x6, 0x88]
        ]

    def connect(self, address, port):
        self.connected = True

    def close(self):
        self.connected = False

    def send_bytes(self, buffer):
        """Doc page 4-8"""
        if not self.connected:
            raise socket.error()
        elif self.does_not_reply:
            pass
        elif buffer[1] == TxSymbol.ENQ.value:
            if self.sends_corrupt_enq_next:
                self.sends_corrupt_enq_next = False
                self._last_response = [TxSymbol.DLE.value, TxSymbol.NAK.value]
                self._on_bytes_received(bytearray([0x00]))
            else:
                self._reply(self._last_response)
                if self._last_message and self._last_response == [TxSymbol.DLE.value, TxSymbol.ACK.value]:
                    self._reply(self._last_message)
        elif buffer[1] == TxSymbol.NAK.value:
            self._reply(self._last_message)
        elif buffer[1] == TxSymbol.ACK.value and self.sends_corrupt_ack_once:
            self.sends_corrupt_ack_once = False
            self._enq()
        elif buffer[1] == TxSymbol.STX.value:
            if self.force_bad_crc_once:
                self.force_bad_crc_once = False
                buffer = list(buffer)
                buffer[-2:] = [0x00, 0x00]
                buffer = bytearray(buffer)
            if buffer[-2:] == bytearray([0x00, 0x00]) or self.replies_nak:  # forced bad CRC
                self._nak()
            elif self.message_sink_is_full_for_next_nb_commands:
                self.message_sink_is_full_for_next_nb_commands -= 1
                self._nak()
            elif self.always_replies_messages:
                self._sink_message(buffer)
                self._sink_message(buffer)
                self._sink_message(buffer)
            else:
                self._ack()
                self._sink_message(buffer)
        else:
            self._last_response = [TxSymbol.DLE.value, TxSymbol.NAK.value]
            self._last_message = None

    def _sink_message(self, buffer):
        if buffer[4] == 0x0f and buffer[8] == 0xa2:
            table = buffer[10]
            start = buffer[12] * 2  # assume file type is always integer for this mock
            stop = start + buffer[9]
            values = self._tables[table][start:stop]
            tns = buffer[6] & 0xff + buffer[7] << 8
            reply = Reply4f()
            reply.init_with_params(dst=buffer[1], src=buffer[2], tns=tns, data=values)
            buffer = reply.get_bytes()
            self._last_message = buffer
            if self.dont_reply_data_frame:
                self.dont_reply_data_frame = False
            else:
                self._reply(buffer)
        else:  # pragma: nocover
            raise NotImplementedError(buffer)

    def _reply(self, buffer):
        if buffer[1] == TxSymbol.ACK.value and self.replies_ack_timeout_once or self.replies_timeout:
            self.replies_ack_timeout_once = False
            buffer = [0x00]
        elif buffer[1] == TxSymbol.STX.value:
            if self.replies_corrupt_command_once:
                self.replies_corrupt_command_once = False
                buffer = list(buffer)
                buffer[-2:] = [0x00, 0x00]
            elif self.replies_invalid_length_frame_once:
                self.replies_invalid_length_frame_once = False
                buffer = buffer[:5]
        if self.replies_segmented:
            half_index = int(len(buffer) / 2)
            self._on_bytes_received(bytearray(buffer[:half_index]))
            self._on_bytes_received(bytearray(buffer[half_index:]))
        else:
            self._on_bytes_received(bytearray(buffer))

    def _ack(self):
        self._last_response = [TxSymbol.DLE.value, TxSymbol.ACK.value]
        self._reply([TxSymbol.DLE.value, TxSymbol.ACK.value])

    def _nak(self):
        self._last_response = [TxSymbol.DLE.value, TxSymbol.NAK.value]
        self._reply([TxSymbol.DLE.value, TxSymbol.NAK.value])

    def _enq(self):
        self._reply([TxSymbol.DLE.value, TxSymbol.ENQ.value])
