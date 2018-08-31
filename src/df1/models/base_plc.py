# -*- coding: utf-8 -*-

import abc


class BasePlc:
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.bytes_received = []
        self.disconnected = []

    def _on_bytes_received(self, buffer):
        for method in self.bytes_received:
            method(buffer)

    def _on_disconnected(self):
        for method in self.disconnected:
            method()

    @abc.abstractmethod
    def connect(self, address, port): pass  # pragma: nocover

    @abc.abstractmethod
    def close(self): pass  # pragma: nocover

    @abc.abstractmethod
    def send_bytes(self, buffer): pass  # pragma: nocover
