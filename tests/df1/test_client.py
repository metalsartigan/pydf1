# -*- coding: utf-8 -*-

import time
from mock import patch
from unittest import TestCase

from df1.df1_client import Df1Client
from df1.commands import Command0FA2, Command0FAA
from df1.replies import ReplyAck, Reply4f, ReplyNak, ReplyEnq
from df1.models.exceptions import SendReceiveError
from df1.file_type import FileType
from .mocks import MockPlc


class TestClient(TestCase):
    def setUp(self):
        super(TestClient, self).setUp()
        self.plc = MockPlc()
        self._init_mock_tns()
        self.client = Df1Client(plc=self.plc, src=0x0, dst=0x1)
        self.cmd_read = self.client.create_command(Command0FA2, bytes_to_read=0x2,
                                                   table=0x00, file_type=FileType.INTEGER, start=0x01)
        self.cmd_write = self.client.create_command(Command0FAA, data_to_write=[10, 11, 12],
                                                    table=0x00, file_type=FileType.INTEGER, start=0x01)
        self.client.connect('127.0.0.1', 10232)

    def _init_mock_tns(self):
        tns_patcher = patch.object(Df1Client, '_get_initial_tns')
        self.addCleanup(tns_patcher.stop)
        self.mock_tns = tns_patcher.start()
        self.mock_tns.return_value = 0x01

    def test_context_manager(self):
        plc = MockPlc()
        with Df1Client(plc=plc, src=0x0, dst=0x1) as client:
            self.assertFalse(plc.connected)
            client.connect('127.0.0.1', 10232)
            self.assertTrue(plc.connected)
        self.assertFalse(plc.connected)

    def test_create_command(self):
        with patch.object(Df1Client, '_get_new_tns') as mock_new_tns:
            mock_new_tns.return_value = 0x1
            command = self.client.create_command(Command0FA2, bytes_to_read=0x2,
                                                 table=0x01, file_type=FileType.INTEGER, start=0x01)
        expected = bytearray([0x10, 0x2, 0x1, 0x0, 0xf, 0x0, 0x1, 0x0, 0xa2, 0x02, 0x01, 0x89, 0x01, 0x00,
                          0x10, 0x03, 0xbb, 0x70])
        actual = command.get_bytes()
        self.assertEqual(expected, actual)

    def test_send_command_not_connected(self):
        plc = MockPlc()
        with Df1Client(plc=plc, src=0x0, dst=0x1) as client:
            with self.assertRaises(Exception):
                client.send_command(self.cmd_read)

    def test_normal_message_transfer_read(self):
        """Doc page 4-10"""
        reply = self.client.send_command(self.cmd_read)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(4, len(self.client.comm_history))
        self._assert_command(Command0FA2, 'out', 0)
        self._assert_command(ReplyAck, 'in', 1)
        self._assert_command(Reply4f, 'in', 2)
        self._assert_command(ReplyAck, 'out', 3)

    def test_normal_message_transfer_write(self):
        """Doc page 4-10"""
        self.client.send_command(self.cmd_write)
        self.assertEquals(4, len(self.client.comm_history))
        self._assert_command(Command0FAA, 'out', 0)
        self._assert_command(ReplyAck, 'in', 1)
        self._assert_command(Reply4f, 'in', 2)
        self._assert_command(ReplyAck, 'out', 3)

    def _assert_command(self, command_type, direction, index):
        cmd = self.client.comm_history[index]
        self.assertEqual(command_type, type(cmd['command']))
        self.assertEqual(direction, cmd['direction'])

    def test_message_transfer_with_nak(self):
        """Doc page 4-11"""
        self.plc.force_bad_crc_once = True
        reply = self.client.send_command(self.cmd_read)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(6, len(self.client.comm_history))
        self._assert_command(Command0FA2, 'out', 0)
        self._assert_command(ReplyNak, 'in', 1)
        self._assert_command(Command0FA2, 'out', 2)
        self._assert_command(ReplyAck, 'in', 3)
        self._assert_command(Reply4f, 'in', 4)
        self._assert_command(ReplyAck, 'out', 5)

    def test_message_transfer_with_timeout_and_enq(self):
        """Doc page 4-12"""
        self.plc.replies_ack_timeout_once = True
        self.plc.dont_reply_data_frame = True
        with patch.object(time, 'sleep'):
            reply = self.client.send_command(self.cmd_read)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(5, len(self.client.comm_history))

        self._assert_command(Command0FA2, 'out', 0)
        self._assert_command(ReplyEnq, 'out', 1)
        self._assert_command(ReplyAck, 'in', 2)
        self._assert_command(Reply4f, 'in', 3)
        self._assert_command(ReplyAck, 'out', 4)

    def test_message_transfer_with_retransmission(self):
        """Doc page 4-13"""
        self.plc.replies_ack_timeout_once = True
        self.plc.dont_reply_data_frame = True
        self.plc.sends_corrupt_enq_next = True
        with patch.object(time, 'sleep'):
            reply = self.client.send_command(self.cmd_read)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(8, len(self.client.comm_history))

        self._assert_command(Command0FA2, 'out', 0)
        self._assert_command(ReplyEnq, 'out', 1)
        self._assert_command(ReplyEnq, 'out', 2)
        self._assert_command(ReplyNak, 'in', 3)
        self._assert_command(Command0FA2, 'out', 4)
        self._assert_command(ReplyAck, 'in', 5)
        self._assert_command(Reply4f, 'in', 6)
        self._assert_command(ReplyAck, 'out', 7)

    def test_message_transfer_with_message_sink_full(self):
        """Doc page 4-14"""
        self.plc.message_sink_is_full_for_next_nb_commands = 2
        reply = self.client.send_command(self.cmd_read)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(8, len(self.client.comm_history))

        self._assert_command(Command0FA2, 'out', 0)
        self._assert_command(ReplyNak, 'in', 1)
        self._assert_command(Command0FA2, 'out', 2)
        self._assert_command(ReplyNak, 'in', 3)
        self._assert_command(Command0FA2, 'out', 4)
        self._assert_command(ReplyAck, 'in', 5)
        self._assert_command(Reply4f, 'in', 6)
        self._assert_command(ReplyAck, 'out', 7)

    def test_message_transfer_with_nak_on_reply(self):
        """Doc page 4-15"""
        self.plc.replies_corrupt_command_once = True
        reply = self.client.send_command(self.cmd_read)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(6, len(self.client.comm_history))
        self._assert_command(Command0FA2, 'out', 0)
        self._assert_command(ReplyAck, 'in', 1)
        self._assert_command(Reply4f, 'in', 2)
        self._assert_command(ReplyNak, 'out', 3)
        self._assert_command(Reply4f, 'in', 4)
        self._assert_command(ReplyAck, 'out', 5)

    def test_message_transfer_with_timeout_and_enq_for_reply(self):
        """Doc page 4-16"""
        self.plc.sends_corrupt_ack_once = True
        reply = self.client.send_command(self.cmd_read)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(6, len(self.client.comm_history))

        self._assert_command(Command0FA2, 'out', 0)
        self._assert_command(ReplyAck, 'in', 1)
        self._assert_command(Reply4f, 'in', 2)
        self._assert_command(ReplyAck, 'out', 3)
        self._assert_command(ReplyEnq, 'in', 4)
        self._assert_command(ReplyAck, 'out', 5)

    def test_message_transfer_with_message_source_full_on_the_reply(self):
        """Doc page 4-17"""
        """Could never happen unless out of memory."""
        pass

    def test_invalid_length_frame(self):
        self.plc.replies_invalid_length_frame_once = True
        with patch.object(time, 'sleep'):
            reply = self.client.send_command(self.cmd_read)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(5, len(self.client.comm_history))

        self._assert_command(Command0FA2, 'out', 0)
        self._assert_command(ReplyAck, 'in', 1)
        self._assert_command(ReplyNak, 'out', 2)
        self._assert_command(Reply4f, 'in', 3)
        self._assert_command(ReplyAck, 'out', 4)

    def test_reply_timeout(self):
        self.plc.replies_timeout = True
        with patch.object(time, 'sleep'):
            with self.assertRaises(SendReceiveError):
                self.client.send_command(self.cmd_read)

    def test_reply_nak(self):
        self.plc.replies_nak = True
        with self.assertRaises(SendReceiveError):
            self.client.send_command(self.cmd_read)

    def test_no_reply(self):
        self.plc.does_not_reply = True
        with patch.object(time, 'sleep'):
            with self.assertRaises(SendReceiveError):
                self.client.send_command(self.cmd_read)

    def test_multiple_message_replies(self):
        self.plc.always_replies_messages = True
        with self.assertRaises(SendReceiveError):
            with patch.object(time, 'sleep'):
                self.client.send_command(self.cmd_read)

    def test_tns_increment(self):
        self.mock_tns.return_value = 0x10
        plc = MockPlc()
        plc.force_bad_crc_once = True
        with Df1Client(plc=plc, src=0x0, dst=0x1) as client:
            client.connect('127.0.0.1', 10232)
            cmd = client.create_command(Command0FA2, bytes_to_read=0x2,
                                        table=0x00, file_type=FileType.INTEGER, start=0x01)
            self.assertEqual(0x11, cmd.tns)
            client.send_command(cmd)
            self.assertEqual(0x12, cmd.tns)

    def test_tns_wrap(self):
        self.mock_tns.return_value = 0xfffe
        plc = MockPlc()

        def create_cmd():
            return client.create_command(Command0FA2, bytes_to_read=0x2,
                                         table=0x00, file_type=FileType.INTEGER, start=0x01)
        with Df1Client(plc=plc, src=0x0, dst=0x1) as client:
            cmd = create_cmd()
            self.assertEqual(0xffff, cmd.tns)
            cmd = create_cmd()
            self.assertEqual(0x0, cmd.tns)
            cmd = create_cmd()
            self.assertEqual(0x1, cmd.tns)

    def test_frame_segmentation(self):
        self.plc.replies_segmented = True
        reply1 = self.client.send_command(self.cmd_read)
        reply2 = self.client.send_command(self.cmd_read)
        actual1 = reply1.get_data(FileType.INTEGER)
        actual2 = reply2.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual1)
        self.assertEquals([0xe515], actual2)
        self.assertEqual(0, len(self.client._receive_buffer))
