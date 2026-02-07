"""
@module
SMS - Socket
"""

import socket
import threading
import time
from server.system_logger import SLOG


class Socket:
    """Socket Manager"""

    def __init__(self, ip: str, port: int):
        self._ip = ip
        self._port = port
        self._connections = []

    def serve(self, message_handler, condition: bool):
        """Serve"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self._ip, self._port))

            while condition:
                s.listen()

                conn, addr = s.accept()

                print(f"Connected by {addr}")

                connection = Connection(
                    conn,
                    message_handler,
                    lambda: self._connections.remove(connection),
                )

                self._connections.append(connection)
                connection.start()

    def send(self, data):
        """Send message"""
        sock = self._connect()
        Socket.send_framed(sock, data)
        return sock

    def send_and_wait(self, data):
        """Send and wait for data"""
        sock = self.send(data)
        recv = Socket.recv_framed(sock)
        sock.close()
        return recv

    def _connect(self) -> socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._ip, self._port))
        return sock

    @staticmethod
    def _recv_exact(sock: socket.socket, size: int) -> bytes | None:
        """Receive exact number of bytes from socket"""
        buf = b""
        while len(buf) < size:
            chunk = sock.recv(size - len(buf))
            if not chunk:
                return None
            buf += chunk
        return buf

    @staticmethod
    def recv_framed(sock: socket.socket) -> bytes | None:
        """Receive length-prefixed frame"""
        header = Socket._recv_exact(sock, 4)
        if header is None:
            return None
        length = int.from_bytes(header, "big", signed=False)
        if length == 0:
            return b""
        return Socket._recv_exact(sock, length)

    @staticmethod
    def send_framed(sock: socket.socket, data: bytes) -> None:
        """Send length-prefixed frame"""
        sock.sendall(len(data).to_bytes(4, "big", signed=False) + data)


class Connection(threading.Thread):
    """Message receiver once connection has made"""

    def __init__(self, sock: Socket, message_handler, on_close_listener):
        super().__init__(daemon=True)

        self._sock = sock
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._message_handler = message_handler
        self._on_close_listener = on_close_listener

    def run(self):
        while not self._stop_event.is_set():
            data = Socket.recv_framed(self._sock)
            if data is None:
                break
            if not self._message_handler:
                SLOG.error(f"{self._message_handler} is None, Receiver is closed")
                break
            self._message_handler(self._sock, data)
            time.sleep(1)

    def stop(self):
        """Stop thread by setting threading.event"""
        self._stop_event.set()
        self._on_close_listener()
