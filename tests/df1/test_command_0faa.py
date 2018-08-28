from src.df1.models import Command0FAA
from src.df1.models.file_type import FileType
from .base_test_frame import BaseTestFrame


class TestCommand0FAA(BaseTestFrame):
    def test_get_bytes(self):
        frame = Command0FAA()
        frame.init_with_params(src=0x0, dst=0x1, tns=0x3ae4, data_to_write=[1, 2, 3, 4, 5, 100, 101, 102, 103],
                               table=0x7, file_type=FileType.INTEGER, start=0x0)
        expected = bytes([0x10, 0x02, 0x01, 0x00, 0x0f, 0x00, 0xe4, 0x3a, 0xaa, 0x12, 0x07, 0x89, 0x00, 0x00,
                          0x1, 0x0, 0x2, 0x0, 0x3, 0x0, 0x4, 0x0, 0x5, 0x0, 0x64, 0x00, 0x65, 0x0, 0x66, 0x0, 0x67, 0x0,
                          0x10, 0x03, 0x04, 0xcb])
        actual = frame.get_bytes()
        self._assert_bytes_equal(expected, actual)
        self.assertTrue(frame.is_valid())
