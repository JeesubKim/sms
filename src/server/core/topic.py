"""Topic manager which is in charge of certain topic"""
import threading
import time
from collections import deque
from dataclasses import dataclass
from .mode import Mode
from .binlog import TransactionLog
from .acklog import AckLogEntry, AckState, append_acklog


@dataclass
class UnackedMessage:
    message: TransactionLog
    consumer_id: str
    deadline_ms: int


class Topic(threading.Thread):
    """Topic class, each topic will have one topic instance
    Topic class internally queues the message and batch logging
    """

    def __init__(self, mode: Mode):
        super().__init__(daemon=True)
        self._mode = mode
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._q: deque[TransactionLog] = deque()
        self._unacked: dict[str, UnackedMessage] = {}

    def get_mode(self) -> Mode:
        """getter of mode"""
        return self._mode

    def initialize_queue_from_logs(
        self, transactions: list[TransactionLog], ack_entries: list[AckLogEntry]
    ):
        """Initialize queue/unacked state from binlog + acklog"""
        if self._mode != Mode.QUEUE:
            return
        now_ms = int(time.time() * 1000)
        latest: dict[str, AckLogEntry] = {}
        for entry in ack_entries:
            latest[entry.message_id] = entry

        queue: deque[TransactionLog] = deque()
        unacked: dict[str, UnackedMessage] = {}

        for tx in transactions:
            entry = latest.get(tx.header.message_id)
            if entry is None:
                queue.append(tx)
                continue
            if entry.state == AckState.ACKED:
                continue
            if entry.state == AckState.ASSIGNED:
                if entry.deadline_ms > now_ms:
                    unacked[tx.header.message_id] = UnackedMessage(
                        message=tx,
                        consumer_id=entry.consumer_id,
                        deadline_ms=entry.deadline_ms,
                    )
                    continue
                queue.append(tx)
                continue
            # NACKED or EXPIRED
            queue.append(tx)

        self._q = queue
        self._unacked = unacked

    def add_queue(self, message: TransactionLog):
        """add item in the queue (queue mode)"""
        with self._lock:
            self._q.append(message)

    def fetch_broadcast(self, transactions: list[TransactionLog]) -> list[TransactionLog]:
        """Return broadcast payloads directly"""
        return transactions

    def _expire_unacked(self, now_ms: int):
        """Requeue expired unacked messages"""
        expired = []
        for message_id, item in self._unacked.items():
            if item.deadline_ms <= now_ms:
                expired.append(message_id)
        for message_id in expired:
            item = self._unacked.pop(message_id)
            # requeue to front for faster retry
            self._q.appendleft(item.message)
            append_acklog(
                item.message.header.topic,
                AckLogEntry(
                    timestamp_ms=now_ms,
                    message_id=message_id,
                    consumer_id=item.consumer_id,
                    deadline_ms=item.deadline_ms,
                    state=AckState.EXPIRED,
                ),
            )

    def consume_queue(self, consumer_id: str, ack_timeout_ms: int) -> TransactionLog | None:
        """Consume one message in queue mode"""
        now_ms = int(time.time() * 1000)
        with self._lock:
            self._expire_unacked(now_ms)
            if not self._q:
                return None
            message = self._q.popleft()
            self._unacked[message.header.message_id] = UnackedMessage(
                message=message,
                consumer_id=consumer_id,
                deadline_ms=now_ms + ack_timeout_ms,
            )
            append_acklog(
                message.header.topic,
                AckLogEntry(
                    timestamp_ms=now_ms,
                    message_id=message.header.message_id,
                    consumer_id=consumer_id,
                    deadline_ms=now_ms + ack_timeout_ms,
                    state=AckState.ASSIGNED,
                ),
            )
            return message

    def ack_queue(self, message_id: str, consumer_id: str) -> bool:
        """Ack message in queue mode"""
        now_ms = int(time.time() * 1000)
        with self._lock:
            item = self._unacked.get(message_id)
            if not item:
                return False
            if item.consumer_id != consumer_id:
                return False
            self._unacked.pop(message_id)
            append_acklog(
                item.message.header.topic,
                AckLogEntry(
                    timestamp_ms=now_ms,
                    message_id=message_id,
                    consumer_id=consumer_id,
                    deadline_ms=item.deadline_ms,
                    state=AckState.ACKED,
                ),
            )
            return True

    def nack_queue(self, message_id: str, consumer_id: str) -> bool:
        """Nack message in queue mode (requeue)"""
        now_ms = int(time.time() * 1000)
        with self._lock:
            item = self._unacked.get(message_id)
            if not item:
                return False
            if item.consumer_id != consumer_id:
                return False
            self._unacked.pop(message_id)
            self._q.appendleft(item.message)
            append_acklog(
                item.message.header.topic,
                AckLogEntry(
                    timestamp_ms=now_ms,
                    message_id=message_id,
                    consumer_id=consumer_id,
                    deadline_ms=item.deadline_ms,
                    state=AckState.NACKED,
                ),
            )
            return True

    def run(self):
        while not self._stop_event.is_set():
            time.sleep(1)

    def stop(self):
        self._stop_event.set()
