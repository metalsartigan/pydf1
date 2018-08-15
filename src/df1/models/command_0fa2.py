from .base_command import BaseCommand
from .file_type import FileType


class Command0FA2(BaseCommand):
    """
    protected typed logical read/write with three address fields, but without address sub elements
    http://www.plctalk.net/qanda/showthread.php?t=1016
    """
    def init_with_params(self, *, bytes_to_read, table, file_type: FileType, start, **kwargs):
        sanitized_start = self._swap_endian(start)
        data = [bytes_to_read, table, file_type.value]
        data.extend(sanitized_start)
        super().init_with_params(cmd=0x0f, fnc=0xa2, command_data=data, **kwargs)
