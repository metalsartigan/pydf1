# -*- coding: utf-8 -*-

from .command_0fab import Command0FAB


class Command0FABSingleBit(Command0FAB):
    def init_with_params(self, table, file_type, start, bit_position, bit_value, **kwargs):
        bit_mask = pow(2, bit_position)
        data_to_write = [bit_value * bit_mask]
        super(Command0FABSingleBit, self).init_with_params(table, file_type, start, bit_mask, data_to_write, **kwargs)
