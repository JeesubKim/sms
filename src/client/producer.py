from .client import SMSClient
from ..server.core.kernel import Response
from .exception import ConnectionIsNoneException
from ..server.core.socket import Connection
class SMSProducer(SMSClient):
    
    def produce(self, topic:str, message:any) -> Response:
        if self._conn is None:
            raise ConnectionIsNoneException()
        
        # make a protocol
        packet = packet_gen(topic, message)
        response = self._conn.send(packet)

        return response

        #handle ack/nack from the response