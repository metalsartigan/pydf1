from src.df1.models.base_command import BaseCommand
from src.df1.file_type import FileType


class Command0FA2(BaseCommand):
    """
    protected typed logical read with three address fields
    Official doc 7-17
    """
    def init_with_params(self, *, bytes_to_read, table, file_type: FileType, start, start_sub=0x0, **kwargs):
        if start > 0xfe or start_sub > 0xfe or table > 0xfe:  # pragma: nocover
            raise NotImplementedError("Table, start and start sub higher than 0xfe not supported yet.")
        data = [bytes_to_read, table, file_type.value, start, start_sub]
        super().init_with_params(cmd=0x0f, fnc=0xa2, command_data=data, **kwargs)
