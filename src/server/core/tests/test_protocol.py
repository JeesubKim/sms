import unittest

from server.core.protocol import (
    ProtocolHeader,
    ProtocolPayload,
    RequestProtocol,
)
from server.core.encryption import NoneEncyption


class TestProtocol(unittest.TestCase):
    """BaseProtocol Testing"""

    def test_request(self):
        request = RequestProtocol(
            ProtocolHeader(0, 0, NoneEncyption()), ProtocolPayload([])
        )

        serialized = request.serialize()

        self.assertIsNotNone(serialized)
        RequestProtocol.deserialize(serialized)
        StopAsyncIteration

    def test_serialization(self): ...
