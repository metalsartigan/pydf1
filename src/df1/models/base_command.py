from .base_data_frame import BaseDataFrame


class BaseCommand(BaseDataFrame):
    def __init__(self):
        super().__init__()

    def init_with_params(self, *, cmd, fnc=None, command_data=[], **kwargs):
        data = list(command_data)
        if fnc is not None:
            data.insert(0, fnc)
        super().init_with_params(cmd=cmd, data=data, **kwargs)

