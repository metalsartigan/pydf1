# -*- coding: utf-8 -*-

from df1.models.base_data_frame import BaseDataFrame


class FrameFromBuffer(BaseDataFrame):
    def __init__(self, buffer):
        super(BaseDataFrame, self).__init__(buffer=buffer)
