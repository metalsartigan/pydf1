from .base_simple_reply import BaseSimpleReply
from .tx_symbol import TxSymbol


class ReplyEnq(BaseSimpleReply):
    def __init__(self):
        super().__init__(TxSymbol.ENQ)
