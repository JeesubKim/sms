"""SMS Dashboard module to monitor packets"""

import threading
import time

from server.sms_server import SMSServer
from server.util.config import ServerConfig


class SMSDashboard(threading.Thread):
    """SMS Dashboard manager"""

    def __init__(self, config: ServerConfig, sms_server: SMSServer):
        super().__init__(daemon=True)
        self._config = config
        self._sms_server = sms_server
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

    def run(self):
        """Thread runnable function"""
        while not self._stop_event.is_set():
            time.sleep(1)
