"""SMS Client Abstract class"""

import time
from abc import ABC
from server.core.socket import Socket
from server.core.binlog import TransactionLog, TransactionLogHeader, BinLog
from server.util.config import Server

HOST = "Random"
IP = "127.0.0.1"
PORT = 65534


class SMSClient(ABC):
    """Mutual parent class for all type of clients"""

    def __init__(self, host: str, ip: str, port: int):
        self._host = host
        self._ip = ip
        self._port = port
        self._socket_manager: Socket = None
        self.is_listening = False

    def set_is_listening(self, value: bool):
        """Setter"""
        self.is_listening = value

    def merge_topic_payload(self, topic: str, payload: bytes) -> TransactionLog:
        """Default payload generator"""

        return BinLog.transaction_to_bytes(
            TransactionLog(
                header=TransactionLogHeader(
                    timestamp=int(time.time()),
                    topic=topic,
                    producer=Server(host=self._host, ip=self._ip, port=self._port),
                    payload_size=len(payload),
                ),
                data=payload,
            )
        )

    def init(self) -> Socket:
        """Socket connection method"""
        self._socket_manager = Socket(self._ip, self._port)

        return self._socket_manager
