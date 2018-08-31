# -*- coding: utf-8 -*-

from abc import ABCMeta


class BaseFrame:
    __metaclass__ = ABCMeta

    def __init__(self, buffer=[]):
        self.buffer = list(buffer)

    def get_bytes(self):
        return bytearray(self.buffer)
