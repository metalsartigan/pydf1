# -*- coding: utf-8 -*-

from unittest import TestCase

from df1.commands import Command0FA2
from df1.models import ReplyAck, ReplyEnq, ReplyNak
from df1.file_type import FileType
from df1.models.receive_buffer import ReceiveBuffer


class TestReceiveBuffer(TestCase):
    def setUp(self):
        super(TestReceiveBuffer, self).setUp()
        self.buffer = ReceiveBuffer()
        self._init_cmd_bytes()
        self._init_replies_bytes()

    def _init_cmd_bytes(self):
        cmd = Command0FA2()
        cmd.init_with_params(start=1, bytes_to_read=2, table=3, file_type=FileType.INTEGER)
        self.cmd_bytes = cmd.get_bytes()

    def _init_replies_bytes(self):
        self.ack_bytes = ReplyAck().get_bytes()
        self.enq_bytes = ReplyEnq().get_bytes()
        self.nak_bytes = ReplyNak().get_bytes()

    def test_extend(self):
        self.buffer.extend(bytearray([1, 2, 3, 4]))
        self.buffer.extend(bytearray([5, 6]))
        self.assertEqual(bytearray([1, 2, 3, 4, 5, 6]), self.buffer._buffer)

    def test_len(self):
        self.assertEqual(0, len(self.buffer))
        self.buffer.extend(bytearray([1, 2, 3, 4]))
        self.assertEqual(4, len(self.buffer))

    def test_pop_frames(self):
        self.buffer.extend(bytearray([2, 3, 4]))
        self.buffer.extend(self.cmd_bytes)
        self.buffer.extend(bytearray([5, 6, 7]))
        self.buffer.extend(self.cmd_bytes)
        self.buffer.extend(self.cmd_bytes)
        self.buffer.extend(bytearray([8, 9, 10]))
        frames = self._pop_frames()
        self.assertEqual(0, len(self.buffer._buffer))
        self.assertEqual(3, len(frames))
        self.assertEqual(self.cmd_bytes, frames[0])
        self.assertEqual(self.cmd_bytes, frames[1])
        self.assertEqual(self.cmd_bytes, frames[2])
        self.assertEqual(0, len(self.buffer))

    def _pop_frames(self):
        return list(self.buffer.pop_left_frames())

    def test_pop_frames_segmented_crc(self):
        self.buffer.extend(self.cmd_bytes[:-2])
        frames = self._pop_frames()
        self.assertEqual(0, len(frames))
        self.buffer.extend(self.cmd_bytes[-2:])
        frames = self._pop_frames()
        self.assertEqual(1, len(frames))
        self.assertEqual(self.cmd_bytes, frames[0])

    def test_overflow(self):
        with self.assertRaises(OverflowError):
            for __ in range(1000):
                self.buffer.extend(self.cmd_bytes)

    def test_replies(self):
        self.buffer.extend(self.ack_bytes)
        self.buffer.extend(self.enq_bytes)
        self.buffer.extend(self.nak_bytes)
        frames = self._pop_frames()
        self.assertEqual(3, len(frames))
        self.assertEqual(self.ack_bytes, frames[0])
        self.assertEqual(self.enq_bytes, frames[1])
        self.assertEqual(self.nak_bytes, frames[2])

    def test_reply_with_0x10_0x06_in_app_data(self):
        reply4f_bytes = bytearray([0x10, 0x2, 0x0, 0x1, 0x4f, 0x0, 0xec, 0x39, 0x64, 0x0, 0x90, 0x1, 0x79, 0x4, 0x62, 0x7, 0x4b, 0xa, 0x34, 0xd, 0x1d, 0x10, 0x10, 0x6, 0x13, 0xef, 0x15, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0xd8, 0x18, 0x10, 0x3, 0x87, 0x54])
        self.buffer.extend(bytearray(reply4f_bytes))
        frames = self._pop_frames()
        self.assertEqual(1, len(frames))
        self.assertEqual(0, len(self.buffer))
        self.assertEqual(reply4f_bytes, frames[0])

    def test_incomplete_frames(self):
        self.buffer.extend(self.cmd_bytes[:5])
        self.buffer.extend(self.cmd_bytes[:5])
        self.buffer.extend(self.cmd_bytes)
        frames = self._pop_frames()
        self.assertEqual(1, len(frames))
        self.assertEqual(self.cmd_bytes, frames[0])
        self.assertEqual(0, len(self.buffer._buffer))
