from .base_command import BaseCommand


class Command0FA1(BaseCommand):
    """
    protected typed logical read/write with three address fields, but without address sub elements
    http://www.plctalk.net/qanda/showthread.php?t=1016
    """
    def init_with_params(self, *, bytes_to_read, table, file_type, start, **kwargs):
        data = [bytes_to_read, table, file_type.value, start]
        super().init_with_params(cmd=0x0f, fnc=0xa1, command_data=data, **kwargs)
