from src.df1.models.base_command import BaseCommand


class FrameWithDleInData(BaseCommand):
    def __init__(self):
        super().__init__()
        data = [0x10, 0x0, 0x0, 0x0]
        self.init_with_params(dst=0x01, src=0x0, cmd=0x0f, tns=0x5161, fnc=0xa1, command_data=data)
