import select
import socket
import threading
import time
from collections import deque
from threading import Thread

from . import BasePlc
from .exceptions import SendQueueOverflowError

BUFFER_SIZE = 4096
RECEIVE_TIMEOUT = 1
CONNECT_TIMEOUT = 5
SEND_QUEUE_SIZE = 100


class Df1Plc(BasePlc):
    def __init__(self):
        super().__init__()
        self._socket_thread = None
        self._loop = False
        self._address = None
        self._connected = False
        self._plc_socket = None
        self.force_one_socket_thread_loop = False
        self.force_one_queue_send = False
        self.send_queue = deque()
        self._send_queue_lock = threading.Lock()

    def connect(self, address, port):
        if not self._socket_thread:
            self._address = (address, port)
            self._loop = True
            self._socket_thread = Thread(target=self._socket_loop, name="Socket thread")
            self._socket_thread.start()

    def close(self):
        if self._socket_thread:
            self._loop = False
            self._socket_thread.join()
            self._socket_thread = None

    def send_bytes(self, buffer: bytes):
        with self._send_queue_lock:
            if len(self.send_queue) >= SEND_QUEUE_SIZE:
                raise SendQueueOverflowError()
            else:
                self.send_queue.append(buffer)

    def _socket_loop(self):
        while self._loop or self.force_one_socket_thread_loop or self.force_one_queue_send:
            self.force_one_socket_thread_loop = False
            if not self._connected:
                self._create_connected_socket()
            if self._connected:  # reevaluate after connection
                self._send_loop()
                self._receive_bytes()
        self._connected = False
        if self._plc_socket:
            self._close_socket(self._plc_socket)

    def _send_loop(self):
        with self._send_queue_lock:
            while self.send_queue:
                buffer = self.send_queue.popleft()
                self._socket_send(buffer)
                self.force_one_queue_send = False

    def _socket_send(self, buffer):  # pragma: nocover
        self._plc_socket.send(buffer)

    def _socket_recv(self):  # pragma: nocover
        return self._plc_socket.recv(BUFFER_SIZE)

    def _receive_bytes(self):
        in_sockets, out_sockets, ex = select.select([self._plc_socket], [], [], RECEIVE_TIMEOUT)
        if in_sockets:
            try:
                buffer = self._socket_recv()
            except ConnectionResetError:
                buffer = bytes()
            if buffer:
                self._on_bytes_received(buffer)
            else:
                self._close_socket(self._plc_socket)
                self._connected = False
                self._on_disconnected()

    def _create_connected_socket(self):
        plc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        plc_socket.settimeout(CONNECT_TIMEOUT)
        try:
            self._connect_socket(plc_socket, self._address)
            self._connected = True
            self._plc_socket = plc_socket
        except (ConnectionError, socket.timeout, socket.error):
            self._close_socket(plc_socket)
            self._sleep()

    def _connect_socket(self, plc_socket, address):  # pragma: nocover
        plc_socket.connect(address)

    def _close_socket(self, plc_socket):  # pragma: nocover
        plc_socket.close()

    def _sleep(self):  # pragma: nocover
        time.sleep(1)
