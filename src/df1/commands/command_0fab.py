# -*- coding: utf-8 -*-

from .base_command import BaseCommand
from df1.file_type import FileType


class Command0FAB(BaseCommand):
    """
    Protected Typed Logical Write with Mask
    Unofficial. See:
    http://www.iatips.com/pccc_tips.html#slc5_cmds
    http://forums.mrplc.com/index.php?/topic/677-writing-my-own-df1-driver/
    http://iatips.com/docs/DF1%20Protocol%2017706516%20Suppliment.pdf page 12
    """
    def init_with_params(self, table, file_type, start, bit_mask, data_to_write, start_sub=0x0, **kwargs):
        if file_type in [FileType.INTEGER, FileType.BIT]:
            bytes_to_write = [b for i in data_to_write for b in self._swap_endian(i)]
        else:  # pragma: nocover
            raise NotImplementedError()
        if start > 0xfe or start_sub > 0xfe or table > 0xfe:  # pragma: nocover
            raise NotImplementedError("Table, start, and start sub higher than 0xfe not supported yet.")
        data = [len(bytes_to_write), table, file_type.value, start, start_sub]
        data.extend(self._swap_endian(bit_mask))
        data.extend(bytes_to_write)
        super(Command0FAB, self).init_with_params(cmd=0x0f, fnc=0xab, command_data=data, **kwargs)
