# -*- coding: utf-8 -*-

import socket
import unittest

from mock import patch

from df1.models import Df1Plc
from df1.models.exceptions import SendQueueOverflowError


class TestDf1Plc(unittest.TestCase):
    def setUp(self):
        super(TestDf1Plc, self).setUp()
        self.plc = Df1Plc()
        self.received_data = None
        self.plc_has_disconnected = False
        self.plc.bytes_received.append(self._receive_data)
        self.plc.disconnected.append(self._disconnected)

    def tearDown(self):
        super(TestDf1Plc, self).tearDown()
        self.plc.close()

    def _receive_data(self, buffer):
        self.received_data = buffer

    def _disconnected(self):
        self.plc_has_disconnected = True

    @patch.object(Df1Plc, '_socket_recv')
    @patch.object(Df1Plc, '_close_socket')
    @patch.object(Df1Plc, '_connect_socket')
    @patch.object(Df1Plc, '_socket_send')
    def test_send_disconnected(self, mock_send, *args):
        self.plc.connect('127.0.0.1', 666)
        self.plc.close()
        for i in range(4):
            self.plc.send_bytes(bytearray([i]))
        self.assertEqual(0, mock_send.call_count)
        self.plc.connect('127.0.0.1', 666)
        self.plc.close()
        self.assertEqual(4, mock_send.call_count)
        for i in range(4):
            first_positional_argument_after_self = mock_send.mock_calls[i][1][0]
            self.assertEqual(bytearray([i]), first_positional_argument_after_self)

    @patch.object(Df1Plc, '_close_socket')
    @patch.object(Df1Plc, '_socket_recv')
    @patch.object(Df1Plc, '_socket_send')
    @patch.object(Df1Plc, '_connect_socket')
    def test_send_disconnected_overflow(self, *args):
        self.plc.connect('127.0.0.1', 666)
        self.plc.close()
        for i in range(100):
            self.plc.send_bytes(bytearray([i]))
        with self.assertRaises(SendQueueOverflowError):
            self.plc.send_bytes(bytearray([99]))

    @patch.object(Df1Plc, '_socket_recv')
    @patch.object(Df1Plc, '_close_socket')
    @patch.object(Df1Plc, '_socket_send')
    @patch.object(Df1Plc, '_connect_socket')
    def test_send_bytes(self, mock_connect, mock_send, mock_close, mock_recv):
        mock_recv.return_value = bytearray()
        self.plc.connect('127.0.0.1', 666)
        self.plc.send_bytes(bytearray([1, 2, 3, 4, 5]))
        self.plc.close()
        self.assertEqual(('127.0.0.1', 666), mock_connect.mock_calls[0][1][1])
        mock_send.assert_called_with(bytearray([1, 2, 3, 4, 5]))
        mock_close.assert_called()
        self.assertIsNone(self.received_data)

    @patch.object(Df1Plc, '_close_socket')
    @patch.object(Df1Plc, '_connect_socket')
    @patch.object(Df1Plc, '_socket_recv')
    def test_receive_bytes(self, mock_recv, *args):
        expected = bytearray([1, 2, 3, 4, 5])
        mock_recv.return_value = expected
        self.plc.connect('127.0.0.1', 666)
        self.plc.close()  # join thread
        self.assertEqual(expected, self.received_data)

    @patch.object(Df1Plc, '_sleep')
    @patch.object(Df1Plc, '_close_socket')
    @patch.object(Df1Plc, '_connect_socket')
    def test_connection_refused(self, mock_connect, *args):
        mock_connect.side_effect = socket.error()  # TODO: python3 replace with ConnectionError()
        self.plc.connect('127.0.0.1', 666)
        self.plc.close()  # join thread
        mock_connect.assert_called()

    @patch.object(Df1Plc, '_sleep')
    @patch.object(Df1Plc, '_close_socket')
    @patch.object(Df1Plc, '_connect_socket')
    def test_connection_timeout(self, mock_connect, *args):
        mock_connect.side_effect = socket.timeout()
        self.plc.connect('127.0.0.1', 666)
        self.plc.close()  # join thread
        mock_connect.assert_called()

    @patch.object(Df1Plc, '_connect_socket')
    @patch.object(Df1Plc, '_socket_recv')
    def test_connection_dropped(self, mock_recv, *args):
        mock_recv.return_value = bytearray()
        self.plc.connect('127.0.0.1', 666)
        self.plc.close()  # join thread
        self.assertTrue(self.plc_has_disconnected)

    @patch.object(Df1Plc, '_connect_socket')
    @patch.object(Df1Plc, '_socket_recv')
    def test_connection_reset(self, mock_recv, *args):
        err = socket.error()
        import errno
        err.errno = errno.ECONNRESET
        mock_recv.side_effect = err  # TODO: python 3, replace with ConnectionResetError
        self.plc.connect('127.0.0.1', 666)
        self.plc.close()  # join thread
        self.assertTrue(self.plc_has_disconnected)

    @patch.object(Df1Plc, '_connect_socket')
    @patch.object(Df1Plc, '_socket_recv')
    @patch.object(Df1Plc, '_wait_for_thread')
    def test_thread_start_timeout(self, mock_wait, *args):
        mock_wait.return_value = False
        from df1.models.exceptions import ThreadError
        with self.assertRaisesRegexp(ThreadError, "could not be started"):
            self.plc.connect('127.0.0.1', 666)
