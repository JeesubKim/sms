"""SMS server module"""

import threading
import time
import json
import base64
from uuid import uuid4
from server.util.config import ServerConfig
from server.core.socket import Socket
from server.core.topic import Topic
from server.core.binlog import read_bin, append_bin, TransactionLog, TransactionLogHeader
from server.core.acklog import read_acklog
from server.util.config import Server


class SMSServer(threading.Thread):
    """SMS Server manager"""

    def __init__(self, config: ServerConfig):
        super().__init__(daemon=True)
        self._config = config
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._conn = None
        self._topics: dict[str:Topic] = {}

    def run(self):
        """Thread runnable function"""

        # init topics based on configs
        for topic in self._config.topics:
            self._topics[topic.name] = Topic(topic.mode)

        # read bin files and setup topics
        for name, topic in self._topics.items():
            binlog = read_bin(name)
            if topic.get_mode().name.lower() == "queue":
                ack_entries = read_acklog(name)
                topic.initialize_queue_from_logs(binlog.get_transactions(), ack_entries)

        # init tcp server
        self._conn = Socket(self._config.socket.ip, self._config.socket.port)
        self._conn.serve(self.message_handler, not self._stop_event.is_set())

    def _response(self, status: str, **kwargs):
        payload = {"status": status}
        payload.update(kwargs)
        return json.dumps(payload).encode("utf-8")

    def message_handler(self, socket, data: any):
        """Message handler when new message arrives"""
        try:
            request = json.loads(data.decode("utf-8"))
        except Exception:
            Socket.send_framed(socket, self._response("error", error="invalid_json"))
            return None

        req_type = request.get("type")
        topic_name = request.get("topic")
        if not req_type or not topic_name:
            Socket.send_framed(socket, self._response("error", error="missing_type_or_topic"))
            return None

        topic = self._topics.get(topic_name)
        if not topic:
            Socket.send_framed(socket, self._response("error", error="unknown_topic"))
            return None

        mode = topic.get_mode()

        if req_type == "produce":
            payload_b64 = request.get("payload_b64")
            producer = request.get("producer", {})
            if payload_b64 is None:
                Socket.send_framed(socket, self._response("error", error="missing_payload"))
                return None
            try:
                payload = base64.b64decode(payload_b64)
            except Exception:
                Socket.send_framed(socket, self._response("error", error="invalid_payload_b64"))
                return None

            message_id = str(uuid4())
            transaction = TransactionLog(
                header=TransactionLogHeader(
                    timestamp=int(time.time()),
                    topic=topic_name,
                    message_id=message_id,
                    producer=Server(
                        host=str(producer.get("host", "unknown")),
                        ip=str(producer.get("ip", "unknown")),
                        port=int(producer.get("port", 0)),
                    ),
                    payload_size=len(payload),
                ),
                data=payload,
            )
            append_bin(topic_name, transaction)
            if mode.name.lower() == "queue":
                topic.add_queue(transaction)
            Socket.send_framed(
                socket,
                self._response("ok", type="produce_ack", topic=topic_name, message_id=message_id),
            )
            return None

        if req_type == "consume":
            if mode.name.lower() == "broadcast":
                offset = int(request.get("offset", 0))
                binlog = read_bin(topic_name, offset=offset)
                transactions = binlog.get_transactions()
                messages = [
                    {
                        "message_id": t.header.message_id,
                        "timestamp": t.header.timestamp,
                        "payload_b64": base64.b64encode(t.data).decode("utf-8"),
                    }
                    for t in transactions
                ]
                Socket.send_framed(
                    socket,
                    self._response(
                        "ok",
                        type="consume",
                        mode="broadcast",
                        topic=topic_name,
                        messages=messages,
                        next_offset=offset + len(messages),
                    ),
                )
                return None

            if mode.name.lower() == "queue":
                consumer_id = str(request.get("consumer_id", "unknown"))
                ack_mode = str(
                    request.get(
                        "ack_mode",
                        self._config.queue_ack_mode_default,
                    )
                ).lower()
                ack_timeout_ms = int(
                    request.get(
                        "ack_timeout_ms",
                        self._config.queue_ack_timeout_ms,
                    )
                )
                message = topic.consume_queue(consumer_id, ack_timeout_ms)
                if message is None:
                    Socket.send_framed(
                        socket,
                        self._response(
                            "ok", type="consume", mode="queue", topic=topic_name, status="empty"
                        ),
                    )
                    return None

                if ack_mode == "auto":
                    topic.ack_queue(message.header.message_id, consumer_id)

                Socket.send_framed(
                    socket,
                    self._response(
                        "ok",
                        type="consume",
                        mode="queue",
                        topic=topic_name,
                        message={
                            "message_id": message.header.message_id,
                            "timestamp": message.header.timestamp,
                            "payload_b64": base64.b64encode(message.data).decode("utf-8"),
                        },
                    ),
                )
                return None

            Socket.send_framed(socket, self._response("error", error="unsupported_mode"))
            return None

        if req_type == "ack":
            if mode.name.lower() != "queue":
                Socket.send_framed(socket, self._response("error", error="ack_only_for_queue"))
                return None
            consumer_id = str(request.get("consumer_id", "unknown"))
            message_id = str(request.get("message_id", ""))
            if not message_id:
                Socket.send_framed(socket, self._response("error", error="missing_message_id"))
                return None
            ok = topic.ack_queue(message_id, consumer_id)
            if ok:
                Socket.send_framed(
                    socket, self._response("ok", type="ack", topic=topic_name, message_id=message_id)
                )
            else:
                Socket.send_framed(
                    socket, self._response("error", error="ack_failed", message_id=message_id)
                )
            return None

        if req_type == "nack":
            if mode.name.lower() != "queue":
                Socket.send_framed(socket, self._response("error", error="nack_only_for_queue"))
                return None
            consumer_id = str(request.get("consumer_id", "unknown"))
            message_id = str(request.get("message_id", ""))
            if not message_id:
                Socket.send_framed(socket, self._response("error", error="missing_message_id"))
                return None
            ok = topic.nack_queue(message_id, consumer_id)
            if ok:
                Socket.send_framed(
                    socket, self._response("ok", type="nack", topic=topic_name, message_id=message_id)
                )
            else:
                Socket.send_framed(
                    socket, self._response("error", error="nack_failed", message_id=message_id)
                )
            return None

        Socket.send_framed(socket, self._response("error", error="unsupported_type"))
        return None
