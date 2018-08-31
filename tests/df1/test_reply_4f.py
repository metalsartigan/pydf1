# -*- coding: utf-8 -*-

import unittest

from df1.models import Reply4f
from df1.file_type import FileType


class TestReply4f(unittest.TestCase):
    def setUp(self):
        super(TestReply4f, self).setUp()
        self.reply = Reply4f()
        self.reply.init_with_params(dst=0x01, src=0x00, tns=0x1234, data=range(0x4))

    def test_get_data(self):
        data = self.reply.get_data(FileType.INTEGER)
        self.assertEquals([0x100, 0x302], data)

    def test_get_data_odd_odd_number_of_elements(self):
        self.reply.buffer.pop()
        with self.assertRaises(ArithmeticError):
            self.reply.get_data(FileType.INTEGER)
