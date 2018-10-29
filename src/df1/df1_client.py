# -*- coding: utf-8 -*-

from collections import deque
import random
import threading
import time

from .models import frame_factory, Df1Plc, ReplyTimeout, BaseDataFrame
from .models.exceptions import SendReceiveError
from .models.receive_buffer import ReceiveBuffer
from .models.tx_symbol import TxSymbol
from .replies import ReplyAck, ReplyNak, ReplyEnq


class Df1Client:
    def __init__(self, src, dst, plc=None, history_size=20):
        self.comm_history = deque(maxlen=history_size)
        self._src = src
        self._dst = dst
        self._plc = plc or Df1Plc()
        self._plc.bytes_received.append(self._bytes_received)
        self._messages_sink = []
        self._message_sink_lock = threading.Lock()
        self._last_tns = self._get_initial_tns()
        self._ack = ReplyAck()
        self._nak = ReplyNak()
        self._enq = ReplyEnq()
        self._last_response = [TxSymbol.DLE.value, TxSymbol.NAK.value]
        self._receive_buffer = ReceiveBuffer()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._plc:
            self._plc.close()

    def _get_initial_tns(self):  # pragma: nocover
        return random.randint(0, 0xffff)

    def _get_new_tns(self):
        self._last_tns += 1
        if self._last_tns > 0xffff:
            self._last_tns = 0x0
        return self._last_tns

    def create_command(self, command_type, **kwargs):
        command = command_type()
        command.init_with_params(src=self._src, dst=self._dst, tns=self._get_new_tns(), **kwargs)
        return command

    def connect(self, address, port):
        self._plc.connect(address, port)

    def send_command(self, command):
        """Doc page 4-6 Transmitter"""
        for __ in range(3):
            self.comm_history.append({'direction': 'out', 'command': command})
            self._plc.send_bytes(command.get_bytes())
            retry_send = False
            got_ack = False
            i = 0
            while i < 3:
                reply = self._expect_message()
                if type(reply) is ReplyAck:
                    got_ack = True
                    i = 0
                elif type(reply) is ReplyNak:
                    command.tns = self._get_new_tns()
                    retry_send = True
                    break
                elif type(reply) is ReplyTimeout or not reply.is_valid():
                    if got_ack:
                        self._send_nak()
                    else:
                        self._send_enq()
                elif got_ack:
                    return reply
                i += 1
            if not retry_send:
                raise SendReceiveError()
        raise SendReceiveError()

    def _bytes_received(self, buffer):
        """Doc page 4-8"""
        self._receive_buffer.extend(buffer)
        for full_frame in self._receive_buffer.pop_left_frames():
            self._process_frame_buffer(full_frame)

    def _process_frame_buffer(self, buffer):
        message = frame_factory.parse(buffer)
        self.comm_history.append({'direction': 'in', 'command': message})
        if type(message) == ReplyEnq:
            last_response_buffer = bytearray(self._last_response)
            self.comm_history.append({'direction': 'out', 'command': frame_factory.parse(last_response_buffer)})
            self._plc.send_bytes(last_response_buffer)
        elif issubclass(type(message), BaseDataFrame):
            if message.is_valid():
                self._send_ack()
                with self._message_sink_lock:
                    self._messages_sink.append(message)
            else:
                self._send_nak()
        else:
            with self._message_sink_lock:
                self._messages_sink.append(message)
            self._last_response = [TxSymbol.DLE.value, TxSymbol.NAK.value]

    def _expect_message(self):
        for __ in range(40):
            with self._message_sink_lock:
                if self._messages_sink:
                    return self._messages_sink.pop(0)
            time.sleep(0.1)
        return ReplyTimeout()

    def _send_ack(self):
        self._last_response = [TxSymbol.DLE.value, TxSymbol.ACK.value]
        self.comm_history.append({'direction': 'out', 'command': self._ack})
        self._plc.send_bytes(self._ack.get_bytes())

    def _send_nak(self):
        self._last_response = [TxSymbol.DLE.value, TxSymbol.NAK.value]
        self.comm_history.append({'direction': 'out', 'command': self._nak})
        self._plc.send_bytes(self._nak.get_bytes())

    def _send_enq(self):
        self.comm_history.append({'direction': 'out', 'command': self._enq})
        self._plc.send_bytes(self._enq.get_bytes())
