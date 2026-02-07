"""Ack log utility for queue mode persistence"""

import os
import zlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from collections import OrderedDict
from server.util.file import read_bytes_or_create, append_bytes


class AckState(Enum):
    ASSIGNED = 0
    ACKED = 1
    NACKED = 2
    EXPIRED = 3


@dataclass
class AckLogEntry:
    timestamp_ms: int
    message_id: str
    consumer_id: str
    deadline_ms: int
    state: AckState


def _crc32(data: bytes) -> int:
    return zlib.crc32(data) & 0xFFFFFFFF


def serialize_entry(entry: AckLogEntry) -> bytes:
    data = entry.timestamp_ms.to_bytes(8, "big", signed=False)
    data += entry.state.value.to_bytes(1, "big", signed=False)
    data += len(entry.message_id).to_bytes(4, "big", signed=False)
    data += entry.message_id.encode("utf-8")
    data += len(entry.consumer_id).to_bytes(4, "big", signed=False)
    data += entry.consumer_id.encode("utf-8")
    data += entry.deadline_ms.to_bytes(8, "big", signed=False)
    data += _crc32(data).to_bytes(4, "big", signed=False)
    return data


def decode_entries(data: bytes) -> list[AckLogEntry]:
    entries: list[AckLogEntry] = []
    ptr = 0
    total = len(data)

    def _read(n: int) -> bytes | None:
        nonlocal ptr
        if ptr + n > total:
            return None
        out = data[ptr : ptr + n]
        ptr += n
        return out

    while ptr < total:
        start = ptr
        ts_bytes = _read(8)
        if ts_bytes is None:
            break
        state_bytes = _read(1)
        if state_bytes is None:
            break
        msg_len_bytes = _read(4)
        if msg_len_bytes is None:
            break
        msg_len = int.from_bytes(msg_len_bytes, "big", signed=False)
        msg_bytes = _read(msg_len)
        if msg_bytes is None:
            break
        consumer_len_bytes = _read(4)
        if consumer_len_bytes is None:
            break
        consumer_len = int.from_bytes(consumer_len_bytes, "big", signed=False)
        consumer_bytes = _read(consumer_len)
        if consumer_bytes is None:
            break
        deadline_bytes = _read(8)
        if deadline_bytes is None:
            break
        crc_bytes = _read(4)
        if crc_bytes is None:
            break

        crc_expected = int.from_bytes(crc_bytes, "big", signed=False)
        crc_actual = _crc32(data[start : ptr - 4])
        if crc_expected != crc_actual:
            continue

        try:
            state = AckState(int.from_bytes(state_bytes, "big", signed=False))
        except Exception:
            continue

        entries.append(
            AckLogEntry(
                timestamp_ms=int.from_bytes(ts_bytes, "big", signed=False),
                message_id=msg_bytes.decode("utf-8"),
                consumer_id=consumer_bytes.decode("utf-8"),
                deadline_ms=int.from_bytes(deadline_bytes, "big", signed=False),
                state=state,
            )
        )

    return entries


def read_acklog(topic: str) -> list[AckLogEntry]:
    return decode_entries(read_bytes_or_create(get_acklog_path(topic)))


def append_acklog(topic: str, entry: AckLogEntry) -> None:
    append_bytes(get_acklog_path(topic), serialize_entry(entry))


def compact_acklog(topic: str) -> None:
    """Rewrite ack log keeping only the latest state per message_id"""
    path = get_acklog_path(topic)
    entries = decode_entries(read_bytes_or_create(path))
    latest: OrderedDict[str, AckLogEntry] = OrderedDict()
    for entry in entries:
        if entry.message_id in latest:
            del latest[entry.message_id]
        latest[entry.message_id] = entry

    data = b"".join(serialize_entry(e) for e in latest.values())
    tmp_path = f"{path}.tmp"
    Path(tmp_path).parent.mkdir(parents=True, exist_ok=True)
    with open(tmp_path, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)


def get_acklog_path(topic: str, extension: str = "aql") -> str:
    return os.path.join(
        Path(__file__).resolve().parents[1], "acklogs", topic, f"{topic}.{extension}"
    )
