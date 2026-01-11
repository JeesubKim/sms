"""Initial access procedure"""

from server.core.protocol.procedure.base import BaseProcedure


class InitialAccessProcedure(BaseProcedure):
    """InitialAccessProcedure to connect via socket"""

    # 1. Client -> Server: AccessProtocol w/ information
    # 2. Server -> Client: AccessResponseProtocol w/ Access approval or denial
    # When it's approved


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
