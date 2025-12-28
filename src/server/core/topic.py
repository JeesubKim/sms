""" Topic manager which is incharge of certain topic """
import threading
import time
from collections import deque
from .mode import Mode

class Topic(threading.Thread):
    """ Topic class, each topic will have one topic instance
        Topic class internally queues the message and batch logging 
    """
    def __init__(self, mode: Mode):
        super().__init__(daemon=True)
        self._mode = mode
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._q = deque()
    def get_mode(self) -> Mode:
        """ getter of mode """
        return self._mode

    def add_queue(self, message):
        """ add item in the queue """
        with self._lock:
            self._q.appendleft(message)
        
    def fetch_queue(self, offset:int):
        """ read binlog file """
        response = self._logger.read(offset)
        return response
    

    def run(self):

        while not self._stop_event.is_set():
            
            # pop data from memory and store it as bin file
            time.sleep(1)

    def stop(self):
        self._stop_event.set()