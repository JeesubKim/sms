from .client import SMSClient
from .exception import ConnectionIsNoneException
import time

class SMSConsumer(SMSClient):
    def consume_once(self, topic, offset):
        if self._conn is None:
            raise ConnectionIsNoneException()
        
        packet = packet_gen(CONSUMER, topic, offset)

        recv = self._conn.send_and_wait()

        return recv
    
    def consume_listening(self, topic:str, callback):
        if self._conn is None:
            raise ConnectionIsNoneException()
        
        packet = packet_gen(CONSUMER, topic, offset)


        sock = self._conn.send(packet)
        self.is_listening = True
        
        while self.is_listening:
            recv = sock.recv(1024)
            callback(recv)
            time.sleep(1)

        sock.close()