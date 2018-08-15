from src.df1.models.base_command import BaseCommand


class OfficialTestFrame(BaseCommand):
    """As found in the official AB docs, page 5-7"""
    def __init__(self):
        super().__init__()
        data = [0x00] * 11
        self.init_with_params(dst=0x07, src=0x11, cmd=0x41, tns=0xb953, fnc=0x0, command_data=data)
