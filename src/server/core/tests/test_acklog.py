"""Ack log persistence tests"""

import time
import unittest
from server.core.acklog import (
    AckLogEntry,
    AckState,
    append_acklog,
    read_acklog,
    compact_acklog,
    get_acklog_path,
)
from server.core.topic import Topic
from server.core.binlog import TransactionLog, TransactionLogHeader
from server.util.config import Server
from server.core.mode import Mode


class TestAckLog(unittest.TestCase):
    def setUp(self):
        self.topic = f"test_acklog_{int(time.time() * 1000)}"

    def test_compact_acklog_keeps_latest_state(self):
        now_ms = int(time.time() * 1000)
        append_acklog(
            self.topic,
            AckLogEntry(
                timestamp_ms=now_ms,
                message_id="m1",
                consumer_id="c1",
                deadline_ms=now_ms + 1000,
                state=AckState.ASSIGNED,
            ),
        )
        append_acklog(
            self.topic,
            AckLogEntry(
                timestamp_ms=now_ms + 1,
                message_id="m1",
                consumer_id="c1",
                deadline_ms=now_ms + 1000,
                state=AckState.ACKED,
            ),
        )
        append_acklog(
            self.topic,
            AckLogEntry(
                timestamp_ms=now_ms + 2,
                message_id="m2",
                consumer_id="c2",
                deadline_ms=now_ms + 2000,
                state=AckState.ASSIGNED,
            ),
        )

        compact_acklog(self.topic)
        entries = read_acklog(self.topic)
        # Only latest entry per message_id should remain
        by_id = {e.message_id: e for e in entries}
        self.assertEqual(len(by_id), 2)
        self.assertEqual(by_id["m1"].state, AckState.ACKED)
        self.assertEqual(by_id["m2"].state, AckState.ASSIGNED)

    def test_initialize_queue_from_logs(self):
        now_ms = int(time.time() * 1000)
        tx1 = TransactionLog(
            header=TransactionLogHeader(
                timestamp=int(time.time()),
                topic=self.topic,
                message_id="m1",
                producer=Server("p", "127.0.0.1", 1),
                payload_size=3,
            ),
            data=b"one",
        )
        tx2 = TransactionLog(
            header=TransactionLogHeader(
                timestamp=int(time.time()),
                topic=self.topic,
                message_id="m2",
                producer=Server("p", "127.0.0.1", 1),
                payload_size=3,
            ),
            data=b"two",
        )
        tx3 = TransactionLog(
            header=TransactionLogHeader(
                timestamp=int(time.time()),
                topic=self.topic,
                message_id="m3",
                producer=Server("p", "127.0.0.1", 1),
                payload_size=5,
            ),
            data=b"three",
        )

        ack_entries = [
            AckLogEntry(
                timestamp_ms=now_ms - 100,
                message_id="m1",
                consumer_id="c1",
                deadline_ms=now_ms + 10000,
                state=AckState.ASSIGNED,
            ),
            AckLogEntry(
                timestamp_ms=now_ms - 100,
                message_id="m2",
                consumer_id="c2",
                deadline_ms=now_ms - 1,
                state=AckState.ASSIGNED,
            ),
            AckLogEntry(
                timestamp_ms=now_ms - 100,
                message_id="m3",
                consumer_id="c3",
                deadline_ms=now_ms + 10000,
                state=AckState.ACKED,
            ),
        ]

        topic = Topic(Mode.QUEUE)
        topic.initialize_queue_from_logs([tx1, tx2, tx3], ack_entries)

        # m1 should be unacked, m2 should be queued (expired), m3 dropped (acked)
        consumed = topic.consume_queue("cX", 1000)
        self.assertIsNotNone(consumed)
        self.assertEqual(consumed.header.message_id, "m2")

