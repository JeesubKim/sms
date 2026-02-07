"""Procedure test"""

import time
import unittest
from server.core.protocol.procedure.base import SystemType, BaseProcedure
from server.core.protocol.procedure.basic import InitialAccessProcedure


class TestBaseProcedure(BaseProcedure):
    """Test mock class which extends BaseProcedure"""

    def __init__(self):
        super().__init__(SystemType.SERVER)
        self.called = 0

    def run_impl_server(self):
        self.called += 1

    def run_impl_client(self):
        pass


class TestProcedure(unittest.TestCase):
    """BaseProtocol Testing"""

    def test_base_ndi_feature(self):
        """ndi testing"""
        bp = TestBaseProcedure()
        bp.start()
        self.assertFalse(bp.get_ndi())

        bp.handle("abc")
        time.sleep(1.1)
        self.assertTrue(bp.get_ndi())
        bp.handle("def")
        time.sleep(1.1)
        self.assertFalse(bp.get_ndi())
        bp.stop()

        bp.join()

        self.assertEqual(bp.called, 2)

    def test_server_impl(self):
        """run_impl_server testing"""
        bp = TestBaseProcedure()
        bp.start()

        bp.handle("abc")
        time.sleep(1.1)
        bp.handle("def")
        time.sleep(1.1)
        bp.stop()
        bp.join()

        self.assertEqual(bp.called, 2)

    # def test_server_initial_procedure(self):
    # procedure is a kind of manager which will automatically handle the protocol procedure based on the type (Client or Server)

    # procedure = InitialAccessProcedure(SystemType.SERVER)
    # procedure.start()
    # # procedure is kind of separated thread that handles each procedure
    # # which means if procedure is initiated, it will create its thread, and check
    # # procedure always have to have its own timer

    # procedure.handle()

    # When Client tries to access to the server, client initiate this procedure.
    # When it starts, it should send
