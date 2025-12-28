from abc import ABC
from dataclasses import dataclass
from uuid import uuid4, UUID
from .mode import Mode
from .kernel import Source


class Protocol(ABC):
    def parse(self, payload):
        raise NotImplementedError()
    
class SMSObjectProtocol(Protocol):
    def parse(self, payload):
        return (
            payload.timestamp,
            payload.topic,
            payload.message_id,
            payload.mode,
            payload.source,
            payload.message
        )
    
@dataclass
class Payload:
    timestamp: int
    topic: str
    message_id: UUID
    mode: Mode
    source: Source
    message: any



@dataclass
class TopicIsEmpty(Payload):...