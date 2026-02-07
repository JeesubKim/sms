"""Consumer module"""

from exception import SocketIsNoneException
from .sms_client import SMSClient


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
    def consume_broadcast(self, topic: str, offset: int = 0) -> dict:
        if self._socket_manager is None:
            raise SocketIsNoneException()
        payload = {"type": "consume", "topic": topic, "mode": "broadcast", "offset": offset}
        return self._send_request(payload)

    def consume_queue(
        self,
        topic: str,
        consumer_id: str,
        ack_mode: str | None = None,
        ack_timeout_ms: int | None = None,
    ) -> dict:
        if self._socket_manager is None:
            raise SocketIsNoneException()
        payload = {
            "type": "consume",
            "topic": topic,
            "mode": "queue",
            "consumer_id": consumer_id,
        }
        if ack_mode is not None:
            payload["ack_mode"] = ack_mode
        if ack_timeout_ms is not None:
            payload["ack_timeout_ms"] = ack_timeout_ms
        return self._send_request(payload)

    def ack(self, topic: str, consumer_id: str, message_id: str) -> dict:
        if self._socket_manager is None:
            raise SocketIsNoneException()
        payload = {
            "type": "ack",
            "topic": topic,
            "mode": "queue",
            "consumer_id": consumer_id,
            "message_id": message_id,
        }
        return self._send_request(payload)

    def nack(self, topic: str, consumer_id: str, message_id: str) -> dict:
        if self._socket_manager is None:
            raise SocketIsNoneException()
        payload = {
            "type": "nack",
            "topic": topic,
            "mode": "queue",
            "consumer_id": consumer_id,
            "message_id": message_id,
        }
        return self._send_request(payload)
