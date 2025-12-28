from abc import ABC
from enum import Enum
from .logger import Logger

class Mode(Enum):
    BROADCAST = 0
    QUEUE = 1


class TransactionPolicy(ABC):
    def __init__(self, mode:Mode, logger:Logger):
        self._mode = mode
        self._logger = logger

    def produce(self, message):
        raise NotImplementedError()
    
    def consume(self):
        raise NotImplementedError()
    
    
class BroadcastTransactionPolicy(TransactionPolicy):
    def produce(self, message):
        ...
    
    def consume(self):
        ...
    
