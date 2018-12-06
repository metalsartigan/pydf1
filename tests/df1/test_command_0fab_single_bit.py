# -*- coding: utf-8 -*-

from df1.commands import Command0FABSingleBit
from df1.file_type import FileType
from .base_test_frame import BaseTestFrame


class TestCommand0FABSingleBit(BaseTestFrame):
    def test_get_bytes_true(self):
        frame = Command0FABSingleBit()
        frame.init_with_params(src=0x0, dst=0x1, tns=0x3ae4,
                               table=7, file_type=FileType.INTEGER, start=30, bit_position=3, bit_value=True)
        expected = bytearray([0x10, 0x02, 0x01, 0x00, 0x0f, 0x00, 0xe4, 0x3a, 0xab, 0x02, 0x07, 0x89, 0x1e, 0x0,
                              0x8, 0x0, 0x8, 0x0, 0x10, 0x03, 0x80, 0xfc])
        actual = frame.get_bytes()
        self._assert_bytes_equal(expected, actual)
        self.assertTrue(frame.is_valid())

    def test_get_bytes_false(self):
        frame = Command0FABSingleBit()
        frame.init_with_params(src=0x0, dst=0x1, tns=0x3ae4,
                               table=7, file_type=FileType.INTEGER, start=30, bit_position=3, bit_value=False)
        expected = bytearray([0x10, 0x02, 0x01, 0x00, 0x0f, 0x00, 0xe4, 0x3a, 0xab, 0x02, 0x07, 0x89, 0x1e, 0x0,
                              0x8, 0x0, 0x0, 0x0, 0x10, 0x03, 0x01, 0x3e])
        actual = frame.get_bytes()
        self._assert_bytes_equal(expected, actual)
        self.assertTrue(frame.is_valid())
