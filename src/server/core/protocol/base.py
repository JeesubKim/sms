"""Protocol"""

from abc import ABC
from typing import Self
from dataclasses import dataclass
from enum import Enum
import base64


@dataclass
class ProtocolHeader:
    """Protocol default header"""

    message_id: str
    repeat: int = 0  # 0 means no repeat
    # encryption: BaseEncryption

    def to_dict(self) -> dict:
        "serialization"
        return {
            "__name__": self.__class__.__name__,
            "message_id": self.message_id,
            "repeat": self.repeat,
            # "encryption": self.encryption.to_dict(),
        }

    @classmethod
    def from_dict(cls, data) -> Self:
        """deserialization"""
        # return cls(
        #     message_id=data["message_id"],
        #     repeat=data["repeat"],
        #     encryption=BaseEncryption.from_dict(data["encryption"]),
        # )
        return cls(
            message_id=data["message_id"],
            repeat=data["repeat"],
        )


@dataclass
class ProtocolRequestHeader(ProtocolHeader):
    """Protocol Request Header"""


@dataclass
class ProtocolResponseHeader(ProtocolHeader):
    """Protocol Response Header"""


@dataclass
class ProtocolPayload:
    """Payload"""

    data: bytes

    def to_dict(self) -> dict:
        """serialization"""

        return {
            "__name__": self.__class__.__name__,
            "data": base64.b64encode(self.data).decode("utf-8"),
        }

    @classmethod
    def from_dict(cls, data) -> Self:
        """deserialization"""
        return cls(data=base64.b64decode(data["data"]))


@dataclass
class BaseProtocol(ABC):
    """Base, serializable"""

    header: ProtocolHeader
    payload: ProtocolPayload

    def to_dict(self):
        """serialization"""
        return {
            "__name__": self.__class__.__name__,
            "header": self.header.to_dict(),
            "payload": self.payload.to_dict(),
        }

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
