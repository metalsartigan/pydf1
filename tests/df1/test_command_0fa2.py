# -*- coding: utf-8 -*-

from df1.commands import Command0FA2
from df1.file_type import FileType
from .base_test_frame import BaseTestFrame


class TestCommand0FA2(BaseTestFrame):
    def test_get_bytes(self):
        frame = Command0FA2()
        frame.init_with_params(src=0x0, dst=0x1, tns=0x3ae4, bytes_to_read=20, table=0x7,
                               file_type=FileType.INTEGER, start=0xfe, start_sub=0xb3)
        expected = bytearray([0x10, 0x02, 0x01, 0x00, 0x0f, 0x00, 0xe4, 0x3a, 0xa2, 0x14, 0x07, 0x89, 0xfe, 0xb3,
                          0x10, 0x03, 0x01, 0x79])
        actual = frame.get_bytes()
        self._assert_bytes_equal(expected, actual)
        self.assertTrue(frame.is_valid())
