import unittest
from ..kernel import SMSKernel, AckNack, Source

# from ..protocol.base import SMSObjectProtocol, Payload
from uuid import uuid4
from ..mode import Mode


class TestKernel(unittest.TestCase):

    def test_message_handler(self): ...

    # test_payload = Payload(
    #     123542545,
    #     "test",
    #     uuid4(),
    #     Mode.BROADCAST,
    #     Source.CONSUMER,
    #     ["test", "payloads"],
    # )
    # kernel = SMSKernel(SMSObjectProtocol())
    # response = kernel.message_handler(test_payload)

    # self.assertIsNotNone(response)
    # self.assertIsInstance(response._acknack, AckNack)
    # self.assertTrue(response._acknack.ack)
    # self.assertIsNotNone(response.get_data())
