from .base_test_frame import BaseTestFrame
from .dummy_frames import FrameWithDleInData, FrameWithoutData, OfficialTestFrame, FrameFromBuffer


class TestFrame(BaseTestFrame):
    def test_get_bytes_official_test_frame(self):
        frame = OfficialTestFrame()
        expected = bytes([0x10, 0x02, 0x07, 0x11, 0x41, 0x00, 0x53, 0xb9, 0x0, 0x0, 0x0, 0x0,
                          0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x10, 0x03, 0x6b, 0x4c])
        actual = frame.get_bytes()
        self._assert_bytes_equal(expected, actual)
        self.assertTrue(frame.is_valid())

    def test_get_bytes_dle_in_data(self):
        frame = FrameWithDleInData()
        expected = bytes([0x10, 0x2, 0x1, 0x0, 0xf, 0x0, 0x61, 0x51, 0xa1,
                          0x10, 0x10, 0x0, 0x0, 0x0, 0x10, 0x3, 0xd2, 0x61])
        actual = frame.get_bytes()
        self._assert_bytes_equal(expected, actual)
        self.assertTrue(frame.is_valid())

    def test_get_bytes_no_application_data(self):
        frame = FrameWithoutData()
        expected = bytes([0x10, 0x2, 0x1, 0x0, 0xf, 0x0, 0x61, 0x51, 0xa1, 0x10, 0x3, 0xb6, 0x8f])
        actual = frame.get_bytes()
        self._assert_bytes_equal(expected, actual)
        self.assertTrue(frame.is_valid())

    def test_from_buffer(self):
        buffer = [0x10, 0x2, 0x1, 0x0, 0xf, 0x0, 0x61, 0x51, 0xa1,
                  0x10, 0x10, 0x0, 0x0, 0x0, 0x10, 0x3, 0xd2, 0x61]
        frame = FrameFromBuffer(buffer=buffer)
        self.assertTrue(frame.is_valid())
        frame2 = FrameFromBuffer(buffer=frame.get_bytes())
        self.assertTrue(frame2.is_valid())
