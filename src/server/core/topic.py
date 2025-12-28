from .mode import Mode
import threading
import time
from collections import deque
class Topic(threading.Thread):
    def __init__(self, mode: Mode):
        super().__init__(daemon=True)
        self._mode = mode
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._q = deque()
    def get_mode(self) -> Mode:
        return self._mode

    def add_queue(self, message):
        with self.lock:
            self._q.appendleft(message)
        
    def fetch_queue(self, offset:int):
        response = self._logger.read(offset)
        return response
    

    def run(self):

        while not self._stop_event.is_set():
            
            # pop data from memory and store it as bin file
            time.sleep(1)

    def stop(self):
        self._stop_event.set()