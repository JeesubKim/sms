"""Encryption module"""

from abc import ABC, abstractmethod
from typing import Self
from server.core.protocol import ProtocolPayload


class BaseEncryption(ABC):
    """Base Encryption"""

    @abstractmethod
    def encrypt(self, payload: ProtocolPayload) -> ProtocolPayload:
        """Ecrypt message"""
        raise NotImplementedError()

    @abstractmethod
    def get_module_name(self) -> str:
        """Module name which must be unique"""
        raise NotImplementedError()

    def to_dict(self):
        """serialization"""
        return {"module_name": self.get_module_name()}

    @classmethod
    def from_dict(cls, data) -> Self:
        """deserialization"""
        if data == "encryption.none_encryption":
            return NoneEncyption
        else:
            raise Exception()


class NoneEncyption(BaseEncryption):
    """NoneEncryption"""

    def get_module_name(self) -> str:
        return "encryption.none_encryption"

    def encrypt(self, payload: ProtocolPayload) -> ProtocolPayload:
        return payload
