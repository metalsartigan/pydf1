from src.df1.models.base_data_frame import BaseDataFrame


class FrameFromBuffer(BaseDataFrame):
    def __init__(self, buffer):
        super().__init__(buffer=buffer)
