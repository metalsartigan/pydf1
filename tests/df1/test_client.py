import time
from mock import patch
from unittest import TestCase

from src.df1.df1_client import Df1Client
from src.df1.models.exceptions import SendReceiveError
from .mocks.mock_plc import MockPlc
from src.df1.models import Command0FA2, ReplyAck, Reply4f, ReplyNak, ReplyTimeout, ReplyEnq, InvalidLengthFrame
from src.df1.models.file_type import FileType


class TestClient(TestCase):
    def setUp(self):
        super().setUp()
        self.plc = MockPlc()
        self.cmd = Command0FA2()
        self.cmd.init_with_params(dst=0x01, src=0x00, tns=0x1234, bytes_to_read=0x2,
                                  table=0x00, file_type=FileType.INTEGER, start=0x01)
        self.client = Df1Client(plc=self.plc, src=0x0, dst=0x1)
        self.client.connect('127.0.0.1', 10232)

    def test_context_manager(self):
        plc = MockPlc()
        with Df1Client(plc=plc, src=0x0, dst=0x1) as client:
            self.assertFalse(plc.connected)
            client.connect('127.0.0.1', 10232)
            self.assertTrue(plc.connected)
        self.assertFalse(plc.connected)

    def test_create_command(self):
        command = self.client.create_command(Command0FA2, bytes_to_read=0x2, table=0x01, file_type=FileType.INTEGER, start=0x01)
        expected = bytes([0x10, 0x2, 0x1, 0x0, 0xf, 0x0, 0x1, 0x0, 0xa2, 0x02, 0x01, 0x89, 0x01, 0x00, 0x10, 0x03, 0xbb, 0x70])
        actual = command.get_bytes()
        self.assertEqual(expected, actual)

    def test_send_command_not_connected(self):
        plc = MockPlc()
        with Df1Client(plc=plc, src=0x0, dst=0x1) as client:
            with self.assertRaises(Exception):
                client.send_command(self.cmd)

    def test_normal_message_transfer(self):
        """Doc page 4-10"""
        reply = self.client.send_command(self.cmd)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(4, len(self.client.comm_history))
        self.assertEquals(Command0FA2, type(self.client.comm_history[0]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[1]))
        self.assertEquals(Reply4f, type(self.client.comm_history[2]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[3]))

    def test_message_transfer_with_nak(self):
        """Doc page 4-11"""
        self.plc.force_bad_crc_once = True
        reply = self.client.send_command(self.cmd)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(6, len(self.client.comm_history))
        self.assertEquals(Command0FA2, type(self.client.comm_history[0]))
        self.assertEquals(ReplyNak, type(self.client.comm_history[1]))
        self.assertEquals(Command0FA2, type(self.client.comm_history[2]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[3]))
        self.assertEquals(Reply4f, type(self.client.comm_history[4]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[5]))

    def test_message_transfer_with_timeout_and_enq(self):
        """Doc page 4-12"""
        self.plc.replies_ack_timeout_once = True
        self.plc.dont_reply_data_frame = True
        reply = self.client.send_command(self.cmd)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(6, len(self.client.comm_history))
        self.assertEquals(Command0FA2, type(self.client.comm_history[0]))
        self.assertEquals(ReplyTimeout, type(self.client.comm_history[1]))
        self.assertEquals(ReplyEnq, type(self.client.comm_history[2]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[3]))
        self.assertEquals(Reply4f, type(self.client.comm_history[4]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[5]))

    def test_message_transfer_with_retransmission(self):
        """Doc page 4-13"""
        self.plc.replies_ack_timeout_once = True
        self.plc.dont_reply_data_frame = True
        self.plc.sends_corrupt_enq_next = True
        reply = self.client.send_command(self.cmd)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(10, len(self.client.comm_history))
        self.assertEquals(Command0FA2, type(self.client.comm_history[0]))
        self.assertEquals(ReplyTimeout, type(self.client.comm_history[1]))
        self.assertEquals(ReplyEnq, type(self.client.comm_history[2]))
        self.assertEquals(ReplyTimeout, type(self.client.comm_history[3]))
        self.assertEquals(ReplyEnq, type(self.client.comm_history[4]))
        self.assertEquals(ReplyNak, type(self.client.comm_history[5]))
        self.assertEquals(Command0FA2, type(self.client.comm_history[6]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[7]))
        self.assertEquals(Reply4f, type(self.client.comm_history[8]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[9]))

    def test_message_transfer_with_message_sink_full(self):
        """Doc page 4-14"""
        self.plc.message_sink_is_full_for_next_nb_commands = 2
        reply = self.client.send_command(self.cmd)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(8, len(self.client.comm_history))
        self.assertEquals(Command0FA2, type(self.client.comm_history[0]))
        self.assertEquals(ReplyNak, type(self.client.comm_history[1]))
        self.assertEquals(Command0FA2, type(self.client.comm_history[2]))
        self.assertEquals(ReplyNak, type(self.client.comm_history[3]))
        self.assertEquals(Command0FA2, type(self.client.comm_history[4]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[5]))
        self.assertEquals(Reply4f, type(self.client.comm_history[6]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[7]))

    def test_message_transfer_with_nak_on_reply(self):
        """Doc page 4-15"""
        self.plc.replies_corrupt_command_once = True
        reply = self.client.send_command(self.cmd)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(6, len(self.client.comm_history))
        self.assertEquals(Command0FA2, type(self.client.comm_history[0]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[1]))
        self.assertEquals(Reply4f, type(self.client.comm_history[2]))
        self.assertEquals(ReplyNak, type(self.client.comm_history[3]))
        self.assertEquals(Reply4f, type(self.client.comm_history[4]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[5]))

    def test_message_transfer_with_timeout_and_enq_for_reply(self):
        """Doc page 4-16"""
        self.plc.sends_corrupt_ack_once = True
        reply = self.client.send_command(self.cmd)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(6, len(self.client.comm_history))
        self.assertEquals(Command0FA2, type(self.client.comm_history[0]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[1]))
        self.assertEquals(Reply4f, type(self.client.comm_history[2]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[3]))
        self.assertEquals(ReplyEnq, type(self.client.comm_history[4]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[5]))

    def test_message_transfer_with_message_source_full_on_the_reply(self):
        """Doc page 4-17"""
        """Could never happen unless out of memory."""
        pass

    def test_invalid_length_frame(self):
        self.plc.replies_invalid_length_frame_once = True
        reply = self.client.send_command(self.cmd)
        actual = reply.get_data(FileType.INTEGER)
        self.assertEquals([0xe515], actual)
        self.assertEquals(6, len(self.client.comm_history))
        self.assertEquals(Command0FA2, type(self.client.comm_history[0]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[1]))
        self.assertEquals(InvalidLengthFrame, type(self.client.comm_history[2]))
        self.assertEquals(ReplyNak, type(self.client.comm_history[3]))
        self.assertEquals(Reply4f, type(self.client.comm_history[4]))
        self.assertEquals(ReplyAck, type(self.client.comm_history[5]))

    def test_reply_timeout(self):
        self.plc.replies_timeout = True
        with self.assertRaises(SendReceiveError):
            self.client.send_command(self.cmd)

    def test_reply_nak(self):
        self.plc.replies_nak = True
        with self.assertRaises(SendReceiveError):
            self.client.send_command(self.cmd)

    def test_no_reply(self):
        self.plc.does_not_reply = True
        with patch.object(time, 'sleep'):
            with self.assertRaises(SendReceiveError):
                self.client.send_command(self.cmd)

    def test_multiple_message_replies(self):
        self.plc.always_replies_messages = True
        with self.assertRaises(SendReceiveError):
            self.client.send_command(self.cmd)
