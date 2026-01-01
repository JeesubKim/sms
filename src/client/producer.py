"""Producer module"""

from exception import SocketIsNoneException
from client.sms_client import SMSClient
from server.core.kernel import Response


class SMSProducer(SMSClient):
    """SMS Producer impl class which extends SMSClient"""

    def produce(self, topic: str, message: bytes) -> Response:
        """Produce message to the topic"""
        if self._socket_manager is None:
            raise SocketIsNoneException()

        # make a protocol
        packet = self.merge_topic_payload(topic, message)
        res = self._socket_manager.send_and_wait(packet)
        return res


if __name__ == "__main__":

    producer = SMSProducer("test_server", "localhost", 9000)
    producer.init()

    response = producer.produce(
        "default_broadcast", "Hello Socket Server?".encode(encoding="utf-8")
    )
    print(response)
