# -*- coding: utf-8 -*-

from df1.models.base_data_frame import BaseDataFrame
from df1.file_type import FileType


class Reply4f(BaseDataFrame):
    def __init__(self, **kwargs):
        super(Reply4f, self).__init__(**kwargs)

    def init_with_params(self, dst, src, tns, data):
        super(Reply4f, self).init_with_params(src=src, dst=dst, cmd=0x4f, tns=tns, data=data)

    def get_data(self, file_type):
        if file_type == FileType.INTEGER:
            data = list(self._get_command_data())
            if len(data) % 2:
                raise ArithmeticError("get_data FileType.INTEGER but data contains odd number of elements.")
            return list(self.__pop_integer_data(data))
        else:  # pragma: nocover
            raise NotImplementedError("Only FileType.INTEGER is implemented at the moment.")

    def __pop_integer_data(self, data):
        data = list(data)
        while data:
            yield (data.pop(0) & 0xff) + (data.pop(0) << 8)
