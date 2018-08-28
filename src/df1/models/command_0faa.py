from .base_command import BaseCommand
from .file_type import FileType


class Command0FAA(BaseCommand):
    """
    protected typed logical write with three address fields
    http://www.plctalk.net/qanda/showthread.php?t=1016
    """
    def init_with_params(self, *, table, file_type: FileType, start, data_to_write, **kwargs):
        if file_type == FileType.INTEGER:
            bytes_to_write = [b for i in data_to_write for b in self._swap_endian(i)]
        else:  # pragma: nocover
            raise NotImplementedError()
        sanitized_start = self._swap_endian(start)
        # convert data to write to list of bytes (si integer. supporter uniquement integer pour linstant.)
        # prendre len de ca pour bytes to write
        data = [len(bytes_to_write), table, file_type.value]
        data.extend(sanitized_start)
        data.extend(bytes_to_write)
        super().init_with_params(cmd=0x0f, fnc=0xaa, command_data=data, **kwargs)
