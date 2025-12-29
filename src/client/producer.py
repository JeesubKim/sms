"""Producer module"""

from src.exception import SocketIsNoneException
from .client import SMSClient
from ..server.core.kernel import Response


class SMSProducer(SMSClient):
    """SMS Producer impl class which extends SMSClient"""

    def produce(self, topic: str, message: bytes) -> Response:
        """Produce message to the topic"""
        if self._sock is None:
            raise SocketIsNoneException()

        # make a protocol
        packet = self.merge_topic_payload(topic, message)
        response = self._sock.send(packet)
        return response
