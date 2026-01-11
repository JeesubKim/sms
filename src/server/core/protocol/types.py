from typing import Self
from dataclasses import dataclass
import json
from server.core.protocol.base import BaseProtocol, ProtocolRequestHeader, Access
from exception import ClassNameDoesNotMatch


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


# @dataclass
# class Payload:
#     timestamp: int
#     topic: str
#     message_id: UUID
#     mode: Mode
#     source: Source
#     message: any


# @dataclass
# class TopicIsEmpty(Payload): ...


PROTOCOL_REGISTRY = {
    "RequestProtocol": RequestProtocol,
    "ResponseProtocol": ResponseProtocol,
    "AuthenticationRequestProtocol": AuthenticationRequestProtocol,
    "AuthenticationResponseProtocol": AuthenticationResponseProtocol,
    "AuthorizationRequestProtocol": AuthorizationRequestProtocol,
    "AuthorizationResponseProtocol": AuthorizationResponseProtocol,
}


def get_base_protocol_class_by_name(data: bytes) -> Self:
    """Class finder"""
    data_dict = json.loads(data.decode("utf-8"))
    classname = data_dict.get("__name__")
    _class = PROTOCOL_REGISTRY.get(classname)
    if classname is None or _class is None:
        raise ClassNameDoesNotMatch()

    return _class
