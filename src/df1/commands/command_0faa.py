# -*- coding: utf-8 -*-

from .base_command import BaseCommand
from df1.file_type import FileType


class Command0FAA(BaseCommand):
    """
    protected typed logical write with three address fields
    Official doc 7-18
    """
    def init_with_params(self, table, file_type, start, data_to_write, start_sub=0x0, **kwargs):
        if file_type == FileType.INTEGER:
            bytes_to_write = [b for i in data_to_write for b in self._swap_endian(i)]
        else:  # pragma: nocover
            raise NotImplementedError()
        if start > 0xfe or start_sub > 0xfe or table > 0xfe:  # pragma: nocover
            raise NotImplementedError("Table, start, and start sub higher than 0xfe not supported yet.")
        data = [len(bytes_to_write), table, file_type.value, start, start_sub]
        data.extend(bytes_to_write)
        super(Command0FAA, self).init_with_params(cmd=0x0f, fnc=0xaa, command_data=data, **kwargs)
