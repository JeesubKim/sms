"""Initial access procedure"""

from server.core.protocol.procedure.base import BaseProcedure
from server.core.protocol.types import AuthenticationRequestProtocol
from server.core.protocol.base import ProtocolHeader, ProtocolPayload
from uuid import uuid4


class InitialAccessProcedure(BaseProcedure):
    """InitialAccessProcedure to connect via socket"""

    # 1. Client -> Server: AccessProtocol w/ information
    # 2. Server -> Client: AccessResponseProtocol w/ Access approval or denial
    # When it's approved
    def run_impl_server(self) -> bool:
        # 2. receive access protocol and check if it's eligible
        # 3. send response back
        # 5. exponal retry param
        pass

    def run_impl_client(self) -> bool:
        # 1. create access protocol and send
        auth_protocol = AuthenticationRequestProtocol(
            ProtocolHeader(message_id=str(uuid4()), repeat=0),  # message_id  # repeat
            ProtocolPayload([]),
        )

        self.sender(auth_protocol)
        wait = True
        while wait:

            time.sleep(1)
        # 4. receive response and record it in the log
        # 5. decide whether to retry
        pass


class HeartBeatProcedure(BaseProcedure):
    """HeartBeat Procedure to check heath"""

    # 1. Client -> Server: HeartBeatProtocol
    # 2. Server -> Client: Response
    # 3. Vice versa


class QueryProcedure(BaseProcedure):
    """Query from client to server and vice versa"""


class Client2ServerQueryProcedure(QueryProcedure):
    """Query from Client to server"""

    # 1. Client -> Server: QueryProtocol
    # 2. Server -> Client: Response


class TopicQueryProcedure(Client2ServerQueryProcedure):
    """Query from consumer to server with topic and offset"""


class Server2ClientQueryProcedure(QueryProcedure):
    """Query from Server to any client, Producer/Consumer"""

    # 1. Client -> Server: QueryProtocol
    # 2. Server -> Client: Response
