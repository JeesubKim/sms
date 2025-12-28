""" Producer module """

from src.exception import ConnectionIsNoneException
from .client import SMSClient
from ..server.core.kernel import Response


class SMSProducer(SMSClient):
    """ SMS Producer impl class which extends SMSClient """

    def produce(self, topic:str, message:any) -> Response:
        """ Produce message to the topic """
        if self._conn is None:
            raise ConnectionIsNoneException()
        
        # make a protocol
        packet = packet_gen(topic, message)
        response = self._conn.send(packet)
        return response