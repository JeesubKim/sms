"""SMS server module"""

import threading
import time
from server.util.config import ServerConfig
from server.core.socket import Connection
from server.core.topic import Topic


class SMSServer(threading.Thread):
    """SMS Server manager"""

    def __init__(self, config: ServerConfig):
        super().__init__(daemon=True)
        self._config = config
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._conn = None
        self._topics = {}

    def run(self):
        """Thread runnable function"""

        # init topics based on configs
        for topic in self._config.topics:
            self._topic[topic.name] = Topic(topic.mode)

        # read bin files and setup topics

        # init tcp server
        self._conn = Connection(self._config.socket.host, self._config.socket.port)
        self._conn.serve(self.message_handler, not self._stop_event.is_set())

    def message_handler(self, data: any):

        return None
