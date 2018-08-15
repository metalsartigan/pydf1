from collections import deque
import threading
import time

from .models import frame_factory, ReplyAck, ReplyNak, BaseSimpleReply, Df1Plc
from .models import ReplyEnq, ReplyTimeout, BaseDataFrame, InvalidLengthFrame
from .models.exceptions import SendReceiveError
from .models.tx_symbol import TxSymbol


class Df1Client:
    def __init__(self, *, src, dst, plc=None, history_size=20):
        self._src = src
        self._dst = dst
        self._plc = plc or Df1Plc()
        self._plc.bytes_received.append(self._bytes_received)
        self._messages_sink = []
        self._message_sink_lock = threading.Lock()
        self._last_tns = 0x00
        self._ack = ReplyAck()
        self._nak = ReplyNak()
        self._enq = ReplyEnq()
        self._last_response = [TxSymbol.DLE.value, TxSymbol.NAK.value]
        self.comm_history = deque(maxlen=history_size)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._plc:
            self._plc.close()

    def create_command(self, command_type, **kwargs):
        command = command_type()
        self._last_tns += 1
        command.init_with_params(src=self._src, dst=self._dst, tns=self._last_tns, **kwargs)
        return command

    def connect(self, address, port):
        self._plc.connect(address, port)

    def send_command(self, command):
        self._message_send_loop(command)
        return self._expect_message()

    def _message_send_loop(self, command):
        """Doc page 4-6 Transmitter"""
        for __ in range(3):
            self.comm_history.append(command)
            self._plc.send_bytes(command.get_bytes())
            retry_send = False
            for ___ in range(3):
                reply = self._expect_reply()
                if type(reply) is ReplyAck:
                    return reply
                elif type(reply) is ReplyNak:
                    retry_send = True
                    break
                elif type(reply) is ReplyTimeout or not reply.is_valid():
                    self._send_enq()
            if not retry_send:
                raise SendReceiveError()
        raise SendReceiveError()

    def _bytes_received(self, buffer):
        """Doc page 4-8"""
        message = frame_factory.parse(buffer)
        self.comm_history.append(message)
        if type(message) == InvalidLengthFrame:
            self._send_nak()
        elif type(message) == ReplyEnq:
            last_response_buffer = bytes(self._last_response)
            self.comm_history.append(frame_factory.parse(last_response_buffer))
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

    def _expect_reply(self):
        for __ in range(3):
            message = self._expect_message()
            if issubclass(type(message), BaseSimpleReply) or type(message) == ReplyTimeout:
                return message
        return ReplyTimeout()

    def _expect_message(self):
        for __ in range(1):
            with self._message_sink_lock:
                if self._messages_sink:
                    return self._messages_sink.pop(0)
            time.sleep(1)
        return ReplyTimeout()

    def _send_ack(self):
        self._last_response = [TxSymbol.DLE.value, TxSymbol.ACK.value]
        self.comm_history.append(self._ack)
        self._plc.send_bytes(self._ack.get_bytes())

    def _send_nak(self):
        self._last_response = [TxSymbol.DLE.value, TxSymbol.NAK.value]
        self.comm_history.append(self._nak)
        self._plc.send_bytes(self._nak.get_bytes())

    def _send_enq(self):
        self.comm_history.append(self._enq)
        self._plc.send_bytes(self._enq.get_bytes())
