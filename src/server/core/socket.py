"""
@module
SMS - Socket
"""

import socket


class Socket:
    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port

    def serve(self, message_handler, condition: bool):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self._host, self._port))

            while condition:
                s.listen()

                conn, addr = s.accept()

                with conn:
                    print(f"Connected by {addr}")
                    while condition:
                        data = conn.recv(1024)
                        message_handler(conn, data)
                        # if not data:
                        #     break
                        # conn.sendall(data)

    def send(self, data):
        sock = self._connect()
        sock.sendall(data)
        return sock

    def send_and_wait(self, data):
        sock = self.send(data)
        recv = sock.recv(1024)
        sock.close()
        return recv

    def _connect(self) -> socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self._host, self._port))
        return sock


class Connection(Socket):
    pass
