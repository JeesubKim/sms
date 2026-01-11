import unittest

from server.core.protocol.base import (
    ProtocolHeader,
    ProtocolPayload,
)
from server.core.protocol.types import (
    RequestProtocol,
    BaseProtocol,
    get_base_protocol_class_by_name,
)
from server.core.encryption import NoneEncyption


class TestProtocol(unittest.TestCase):
    """BaseProtocol Testing"""

    def test_serial_deserialization_of_request_protocol(self):
        """serialization / deserialization test"""
        sample_data = "this is a string type of sample data"
        request = RequestProtocol(
            ProtocolHeader(
                0,  # message_id
                0,  # repeat
            ),
            ProtocolPayload(sample_data.encode("utf-8")),
        )

        serialized = request.serialize()

        self.assertIsNotNone(serialized)

        req_protocol = RequestProtocol.deserialize(serialized)

        self.assertIsInstance(req_protocol, RequestProtocol)
        self.assertEqual(
            req_protocol.payload.data.decode("utf-8"),
            "this is a string type of sample data",
        )

    def test_deserialization(self):
        """"""
        received_data = b'{"__name__": "RequestProtocol", "header": {"__name__": "ProtocolHeader", "message_id": 0, "repeat": 0}, "payload": {"__name__": "ProtocolPayload", "data": "dGhpcyBpcyBhIHN0cmluZyB0eXBlIG9mIHNhbXBsZSBkYXRh"}}'

        _class = get_base_protocol_class_by_name(received_data)

        self.assertIs(_class, RequestProtocol)

    def test_response(self): ...

    def test_serialization(self): ...
