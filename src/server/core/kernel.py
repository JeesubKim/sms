from dataclasses import dataclass
from .mode import Mode
from enum import Enum
from .topic import Topic
from ..system_logger import SLOG
class Source(Enum):
    PRODUCER = 0
    CONSUMER = 1


    
@dataclass
class AckNack:
    topic: Topic
    message_id: int
    ack: bool

@dataclass
class Ack(AckNack):
    ack: bool = True

@dataclass
class Nack(AckNack):
    ack: bool = False

class Response:
    def __init__(self, acknack:AckNack, data:any=None):
        self._acknack = acknack
        self._data = data
        SLOG.info(f"Response:: ack: {self._acknack.ack}, data: {self._data}")
    def get_data(self):
        return self._data
class SMSKernel:
    def __init__(self, protocol):
        self._protocol = protocol
        self._topic = {}
        SLOG.info("SMSKernel is initiated")
        SLOG.info(f"Protocol: {self._protocol}")
    def message_handler(self, payload) -> Response:
        SLOG.info("SMSKernel::message_handler is called")
        # distribute the message to proper topic manager
        (timestamp, topic, message_id, mode, source, message) = self._protocol.parse(payload)
        response_data = None
        SLOG.info(f"topic: {topic}, message_id: {message_id}, mode: {mode}, source: {source}, message: {message}")
        try:
            if not self._topic.get(topic):
                self._topic[topic] = Topic(mode=mode)
            topic_obj:Topic = self._topic[topic]
            # check topic's mode
            mode = topic_obj.get_mode()

            if mode == Mode.BROADCAST:
                if source == Source.PRODUCER:
                    topic_obj.add_queue(message)
                elif source == Source.CONSUMER:
                    response_data = topic_obj.fetch_queue(message)
                # fetch
                
            elif mode == Mode.QUEUE:
                topic_obj.add_queue(message)
                # it is push-based. message will be coming only from the producer

            return Response(Ack(topic, message_id), response_data)
        except Exception as e:
            print(e)

            return Response(Nack(topic, message_id))
        


# producer client -> "produce" ->comm. module -> kernel -> msg handler -> pass to proper topic manager
# topic manager will do something logging



# producer client -> "consume" -> comm. module -> 
