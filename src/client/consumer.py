"""Consumer module"""

from src.exception import SocketIsNoneException
from .sms_client import SMSClient
import time


class SMSConsumer(SMSClient):
    """The way how the consumer consumes the message is diff per Mode"""

    # Broadcast mode
    # consumer should request with topic and offset

    # Queue mode
    # consumer should request with topic only

    # Consumer should know what the mode is?
    # No, consumer can always send offset, server can just ignore it based on the mode set in the topic
    # Is this the right way?
    # It seems not to be the best, but it can reduce the complexity of implementation on the consumer side
    def consume_once(self, topic, offset):
        if self._sock is None:
            raise SocketIsNoneException()

        packet = packet_gen(CONSUMER, topic, offset)

        recv = self._sock.send_and_wait()

        return recv

    def consume_listening(self, topic: str, callback):
        if self._sock is None:
            raise SocketIsNoneException()

        packet = packet_gen(CONSUMER, topic, offset)

        sock = self._sock.send(packet)
        self.is_listening = True

        while self.is_listening:
            recv = sock.recv(1024)
            callback(recv)
            time.sleep(1)

        sock.close()
