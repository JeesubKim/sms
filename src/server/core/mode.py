"""Mode"""

from typing import Self
from abc import ABC
from enum import Enum
from exception import UnexpectedModeStringValue
from .logger import Logger


class Mode(Enum):
    BROADCAST = 0
    QUEUE = 1

    @staticmethod
    def get_from_str(mode_str: str) -> Self:
        match mode_str:
            case "broadcast":
                return Mode.BROADCAST
            case "queue":
                return Mode.QUEUE

            case _:
                raise UnexpectedModeStringValue()


class TransactionPolicy(ABC):
    def __init__(self, mode: Mode, logger: Logger):
        self._mode = mode
        self._logger = logger

    def produce(self, message):
        raise NotImplementedError()

    def consume(self):
        raise NotImplementedError()


class BroadcastTransactionPolicy(TransactionPolicy):
    def produce(self, message): ...

    def consume(self): ...
