"""SMS Client Abstract class"""

import json
from abc import ABC
from server.core.socket import Socket

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

    def _send_request(self, payload: dict) -> dict:
        """Send request as JSON and parse response"""
        if self._socket_manager is None:
            raise Exception("Socket is not initialized")
        response_bytes = self._socket_manager.send_and_wait(
            json.dumps(payload).encode("utf-8")
        )
        return json.loads(response_bytes.decode("utf-8"))

    def init(self) -> Socket:
        """Socket connection method"""
        self._socket_manager = Socket(self._ip, self._port)

        return self._socket_manager
