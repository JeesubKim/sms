"""Protocol"""

from abc import ABC, abstractmethod
from typing import Self
from dataclasses import dataclass
from enum import Enum
import json
from uuid import uuid4, UUID

from server.core.mode import Mode
from server.core.kernel import Source
from server.core.encryption import BaseEncryption


# todo: add class name for serialization and deserialization
"""
@dataclass
class BaseProtocol(ABC):
    header: ProtocolHeader
    payload: ProtocolPayload

    def to_dict(self):
        return {
            "_type": self.__class__.__name__,  # store class name
            "header": self.header.to_dict(),
            "payload": self.payload.to_dict(),
        }

    @classmethod
    def from_dict(cls, data):
        type_name = data.pop("_type", None)
        if type_name and type_name != cls.__name__:
            # dynamically find the subclass
            cls = globals()[type_name]
        return cls(
            header=ProtocolHeader.from_dict(data["header"]),
            payload=ProtocolPayload.from_dict(data["payload"]),
        )

"""


@dataclass
class ProtocolHeader:
    """Protocol default header"""

    message_id: int
    repeat: int = 0  # 0 means no repeat
    encryption: BaseEncryption

    def to_dict(self) -> dict:
        "serialization"
        return {
            "message_id": self.message_id,
            "repeat": self.repeat,
            "encryption": self.encryption.to_dict(),
        }

    @classmethod
    def from_dict(cls, data) -> Self:
        """deserialization"""
        return cls(
            message_id=data["message_id"],
            repeat=data["repeat"],
            encryption=BaseEncryption.from_dict(data["encryption"]),
        )


class ProtocolRequestHeader(ProtocolHeader):
    """Protocol Request Header"""


class ProtocolResponseHeader(ProtocolHeader):
    """Protocol Response Header"""


@dataclass
class ProtocolPayload:
    """Payload"""

    data: bytes

    def to_dict(self) -> dict:
        """serialization"""
        return {"data": self.data}

    @classmethod
    def from_dict(cls, data) -> Self:
        """deserialization"""
        return cls(data=data["data"])


@dataclass
class BaseProtocol(ABC):
    """Base, serializable"""

    header: ProtocolHeader
    payload: ProtocolPayload

    def to_dict(self):
        """serialization"""
        return {"header": self.header.to_dict(), "payload": self.payload.to_dict()}

    @classmethod
    def from_dict(cls, data) -> Self:
        """deserialization"""
        return cls(
            header=ProtocolHeader.from_dict(data["header"]),
            payload=ProtocolPayload.from_dict(data["payload"]),
        )


class Access(Enum):
    """Access"""

    DENIED = 0
    APPROVED = 1


class RequestProtocol(BaseProtocol):
    """Request"""

    header: ProtocolRequestHeader

    def serialize(self) -> bytes:
        """serialize to bytes"""
        return json.dumps(self.to_dict()).encode("utf-8")

    @classmethod
    def deserialize(cls, data: bytes) -> Self:
        """deserialize from bytes"""
        return RequestProtocol.from_dict(json.loads(data.decode("utf-8")))


class ResponseProtocol(BaseProtocol):
    """Response"""


@dataclass
class AuthenticationRequestProtocol(RequestProtocol):
    """Auth request"""


@dataclass
class AuthenticationResponseProtocol(ResponseProtocol):
    """Auth response"""

    access: Access


@dataclass
class AuthorizationRequestProtocol(RequestProtocol):
    """Authorization request"""


@dataclass
class AuthorizationResponseProtocol(ResponseProtocol):
    """Authorization response"""

    access: Access


@dataclass
class Payload:
    timestamp: int
    topic: str
    message_id: UUID
    mode: Mode
    source: Source
    message: any


@dataclass
class TopicIsEmpty(Payload): ...
