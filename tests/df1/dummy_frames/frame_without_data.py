from df1.commands.base_command import BaseCommand


class FrameWithoutData(BaseCommand):
    def __init__(self):
        super(BaseCommand, self).__init__()
        self.init_with_params(expect_reply=False, dst=0x01, src=0x0, cmd=0x0f, tns=0x5161, fnc=0xa1)
