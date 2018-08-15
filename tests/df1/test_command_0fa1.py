from src.df1.models.command_0fa1 import Command0FA1
from src.df1.models.file_type import FileType
from .base_test_frame import BaseTestFrame


class TestCommand0FA1(BaseTestFrame):
    def test_get_bytes(self):
        frame = Command0FA1()
        frame.init_with_params(src=0x0, dst=0x1, tns=0x0001, bytes_to_read=2, table=0x00, file_type=FileType.INTEGER, start=0x0)
        expected = bytes([0x10, 0x2, 0x1, 0x0, 0xf, 0x0, 0x1, 0x00, 0xa1,
                          0x2, 0x0, 0x89, 0x0, 0x10, 0x3, 0xfd, 0x65])
        actual = frame.get_bytes()
        self._assert_bytes_equal(expected, actual)
        self.assertTrue(frame.is_valid())
