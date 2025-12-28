from typing import Self
from ..server.core.socket import Connection
import socket
HOST = "127.0.0.1"
PORT = 65534

class SMSClient:
    def __init__(self, host:str, port:int):
        self._host = host
        self._port = port
        self._conn:Connection = None
        self.is_listening = False
    
    def set_is_listening(self, value:bool):
        self.is_listening = value
