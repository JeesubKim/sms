"""SMS server module"""

import threading
import time
from server.util.config import ServerConfig
from server.core.socket import Socket
from server.core.topic import Topic
from server.core.binlog import read_bin


class SMSServer(threading.Thread):
    """SMS Server manager"""

    def __init__(self, config: ServerConfig):
        super().__init__(daemon=True)
        self._config = config
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._conn = None
        self._topics: dict[str:Topic] = {}

    def run(self):
        """Thread runnable function"""

        # init topics based on configs
        for topic in self._config.topics:
            self._topics[topic.name] = Topic(topic.mode)

        # read bin files and setup topics
        for name, topic in self._topics.items():
            binlog = read_bin(name)
            for transaction in binlog.get_transactions():
                topic.add_queue(transaction)

        # init tcp server
        self._conn = Socket(self._config.socket.ip, self._config.socket.port)
        self._conn.serve(self.message_handler, not self._stop_event.is_set())

    def message_handler(self, socket: Socket, data: any):
        """Message handler when new message arrives"""

        print("received", data)
        socket.send("Hi".encode("utf-8"))
        # parse data
        # pass message to the proper topics
        # send ack or nack using socket
        # based on mode,
        return None
