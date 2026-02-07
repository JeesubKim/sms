"""Producer module"""

from exception import SocketIsNoneException
from client.sms_client import SMSClient
import base64


class SMSProducer(SMSClient):
    """SMS Producer impl class which extends SMSClient"""

    def produce(self, topic: str, message: bytes) -> dict:
        """Produce message to the topic"""
        if self._socket_manager is None:
            raise SocketIsNoneException()

        payload = {
            "type": "produce",
            "topic": topic,
            "payload_b64": base64.b64encode(message).decode("utf-8"),
            "producer": {"host": self._host, "ip": self._ip, "port": self._port},
        }
        return self._send_request(payload)


if __name__ == "__main__":

    producer = SMSProducer("test_server", "localhost", 9000)
    producer.init()

    response = producer.produce(
        "default_broadcast", "Hello Socket Server?".encode(encoding="utf-8")
    )
    print(response)
