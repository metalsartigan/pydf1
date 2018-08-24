from .tx_symbol import TxSymbol


class ReceiveBuffer:
    def __init__(self):
        self._buffer = bytearray()
        self._dle_stx_bytes = bytes([TxSymbol.DLE.value, TxSymbol.STX.value])
        self._dle_etx_bytes = bytes([TxSymbol.DLE.value, TxSymbol.ETX.value])
        self._dle_ack_bytes = bytes([TxSymbol.DLE.value, TxSymbol.ACK.value])
        self._dle_enq_bytes = bytes([TxSymbol.DLE.value, TxSymbol.ENQ.value])
        self._dle_nak_bytes = bytes([TxSymbol.DLE.value, TxSymbol.NAK.value])

    def __len__(self):
        return len(self._buffer)

    def extend(self, other_bytes):
        if len(self._buffer) < 4096:
            self._buffer.extend(other_bytes)
        else:
            raise OverflowError()

    def pop_left_frames(self):
        self._clean_receive_buffer()
        frame_position = self._get_full_frame_position()
        while frame_position:
            frame = self._buffer[frame_position[0]:frame_position[1]]
            del self._buffer[frame_position[0]:frame_position[1]]
            yield frame
            self._clean_receive_buffer()
            frame_position = self._get_full_frame_position()

    def _clean_receive_buffer(self):
        clean = False
        while not clean:
            self._clean_receive_buffer_start()
            clean = True
            if len(self._buffer) >= 2 and self._buffer[:2] == self._dle_stx_bytes:
                next_system_dle_index = self._find_next_system_dle(start=2)
                next_dle_etx_index = self._buffer.find(self._dle_etx_bytes, 2)
                if 0 <= next_system_dle_index < next_dle_etx_index:
                    del self._buffer[:next_system_dle_index]
                    clean = False

    def _find_next_system_dle(self, *, start=0):
        indexes = [
            self._buffer.find(self._dle_stx_bytes, start),
            self._buffer.find(self._dle_ack_bytes, start),
            self._buffer.find(self._dle_enq_bytes, start),
            self._buffer.find(self._dle_nak_bytes, start)
        ]
        return min([i for i in indexes if i >= 0] or [-1])

    def _clean_receive_buffer_start(self):
        if self._buffer:
            if len(self._buffer) > 1 or self._buffer[0] != TxSymbol.DLE.value:
                first_found_index = self._find_next_system_dle()
                if first_found_index == -1:
                    del self._buffer[:]
                elif first_found_index >= 0:
                    del self._buffer[:first_found_index]

    def _get_full_frame_position(self):
        indexes = [
            self._get_stx_etx_frame_position(),
            self._get_short_reply_position(self._dle_ack_bytes),
            self._get_short_reply_position(self._dle_enq_bytes),
            self._get_short_reply_position(self._dle_nak_bytes)
        ]
        return next((i for i in indexes if i is not None), None)

    def _get_short_reply_position(self, reply_bytes):
        index = self._buffer.find(reply_bytes, 0)
        if index >= 0:
            return index, index + 2

    def _get_stx_etx_frame_position(self):
        dle_stx_index = self._buffer.find(self._dle_stx_bytes, 0)
        dle_etx_index = self._buffer.find(self._dle_etx_bytes, 0)
        if dle_stx_index >= 0 and dle_etx_index >= 0 and len(self._buffer) >= (dle_etx_index + 4):
            return dle_stx_index, dle_etx_index + 4
