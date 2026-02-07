"""Base procedure module"""

from abc import abstractmethod
import threading
from enum import Enum
import time


class SystemType(Enum):
    """System type"""

    CLIENT = 0
    SERVER = 1


class BaseProcedure(threading.Thread):
    """Base Procedure"""

    def __init__(
        self,
        system_type: SystemType,
        default_timer: int = 2000,
        steps: list = None,
        callback=None,
    ):
        super().__init__(daemon=True)
        self._system_type = system_type
        self._timer = default_timer  # ms
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._buffer = None
        self._ndi = False
        self._prev_ndi = False
        self.steps = steps if steps else []  # initialization of steps
        self._callback = callback

    def handle(self, data: any):
        """Function to pass data"""
        self._buffer = data
        self._ndi = not self._ndi

    @abstractmethod
    def run_impl_server(self) -> bool:
        """Function to be called in run function, when ndi is toggled"""
        raise NotImplementedError()

    @abstractmethod
    def run_impl_client(self) -> bool:
        """Function to be called in run function, when ndi is toggled"""
        raise NotImplementedError()

    def run(self):
        while not self._stop_event.is_set():
            if self._ndi is not self._prev_ndi:
                # it only processes when new data indicator is toggled
                self._prev_ndi = self._ndi  # update the prev value
                if self._system_type == SystemType.SERVER:
                    self.run_impl_server()
                elif self._system_type == SystemType.CLIENT:
                    self.run_impl_client()
            time.sleep(1)

    def get_ndi(self) -> bool:
        """getter"""
        return self._ndi

    def stop(self):
        """Stop thread"""
        self._stop_event.set()
