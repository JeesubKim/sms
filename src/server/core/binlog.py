"""Bin Log utility"""

import os
import zlib
from typing import Self
from pathlib import Path
from dataclasses import dataclass
from server.util.file import read_bytes_or_create, write_bytes
from server.util.config import Server

"""
Add os.fsync(f.fileno()) after writes for durability

Consider transaction_to_bytes() as @staticmethod

Optionally add file locking (fcntl / msvcrt) for concurrent safety

Use append_bin_reserialize_all() only for rare cases like compaction
"""


@dataclass
class TransactionLogHeader:
    """Transaction Log Header"""

    timestamp: int
    topic: str
    producer: Server
    payload_size: int


@dataclass
class TransactionLog:
    """Transaction Log Object"""

    header: TransactionLogHeader
    data: bytes


class BinLog:
    """Bin Log Object"""

    def __init__(self):
        self._payload_size: int = 0
        self._transactions: list[TransactionLog] = []

    def append(self, transaction: TransactionLog):
        """Append method for transaction"""
        self._payload_size += 1
        self._transactions.append(transaction)

    def append_atomic(self, transaction: TransactionLog):
        """Append transaction to the file immediately"""
        self.append(transaction)

        with open(get_topic_path(transaction.header.topic), "r+b") as f:
            f.seek(0)
            payload_size = int.from_bytes(f.read(4), "big") + 1
            f.seek(0)
            f.write(payload_size.to_bytes(4, "big"))

            f.seek(0, os.SEEK_END)
            f.write(BinLog.transaction_to_bytes(transaction))

    def optimize(self) -> None:
        """Optimize function for the bin"""
        raise NotImplementedError()

    def serialize_all(self) -> bytes:
        """Convert payload_size+transactions into bytes"""
        ret = self._payload_size.to_bytes(4, byteorder="big", signed=False)
        index = []
        for transaction in self._transactions:
            ret += BinLog.transaction_to_bytes(transaction)
        return ret

    def append_index(self):
        """Append index info to the index file"""
        raise NotImplementedError()

    def index_all(self) -> list[int]:
        """Reindexing all transactions"""
        raise NotImplementedError()

    @staticmethod
    def transaction_to_bytes(transaction: TransactionLog) -> bytes:
        """Single Transaction to bytes"""

        transaction_bytes = transaction.header.timestamp.to_bytes(
            4, byteorder="big", signed=False
        )

        transaction_bytes += len(transaction.header.topic).to_bytes(
            4, byteorder="big", signed=False
        )

        # topic
        transaction_bytes += transaction.header.topic.encode("utf-8")

        transaction_bytes += len(transaction.header.producer.host).to_bytes(
            4, byteorder="big", signed=False
        )

        # producer
        transaction_bytes += transaction.header.producer.host.encode("utf-8")

        transaction_bytes += len(transaction.header.producer.ip).to_bytes(
            4, byteorder="big", signed=False
        )
        transaction_bytes += transaction.header.producer.ip.encode("utf-8")

        transaction_bytes += transaction.header.producer.port.to_bytes(
            4, byteorder="big", signed=False
        )

        # payload size
        transaction_bytes += transaction.header.payload_size.to_bytes(
            4, byteorder="big", signed=False
        )

        transaction_bytes += transaction.data

        transaction_bytes += crc32(transaction_bytes).to_bytes(4, "big")

        return transaction_bytes

    def get_size(self) -> int:
        """Getter"""
        return self._payload_size

    def get_transactions(self) -> list[TransactionLog]:
        """Getter"""
        return self._transactions

    def cut(self, offset: int) -> Self:
        """Offset"""
        self._transactions = self._transactions[offset:]
        self._payload_size = len(self._transactions)
        return self

    @staticmethod
    def decode(data: bytes, offset: int = 0) -> Self:
        """Static helper method to decode the bytes"""
        blog = BinLog()
        ptr = 0  # file pointer
        # read bytes, header
        payload_size = int.from_bytes(data[ptr : ptr + 4], byteorder="big")

        ptr += 4

        for _ in range(payload_size):
            start = ptr
            timestamp = int.from_bytes(data[ptr : ptr + 4], byteorder="big")
            ptr += 4

            topic_length = int.from_bytes(data[ptr : ptr + 4], byteorder="big")
            ptr += 4

            topic = data[ptr : ptr + topic_length].decode("utf-8")
            ptr += topic_length

            producer_name_length = int.from_bytes(data[ptr : ptr + 4], byteorder="big")
            ptr += 4
            producer_name = data[ptr : ptr + producer_name_length].decode("utf-8")
            ptr += producer_name_length
            producer_host_length = int.from_bytes(data[ptr : ptr + 4], byteorder="big")
            ptr += 4
            producer_host = data[ptr : ptr + producer_host_length].decode("utf-8")
            ptr += producer_host_length
            producer_port = int.from_bytes(data[ptr : ptr + 4], byteorder="big")
            ptr += 4
            transaction_payload_size = int.from_bytes(
                data[ptr : ptr + 4], byteorder="big"
            )
            ptr += 4

            transaction_data = data[ptr : ptr + transaction_payload_size]

            ptr += transaction_payload_size
            crc = crc32(data[start:ptr])
            stored_crc = int.from_bytes(data[ptr : ptr + 4], byteorder="big")
            ptr += 4

            if crc != stored_crc:
                continue
            blog.append(
                TransactionLog(
                    TransactionLogHeader(
                        timestamp,
                        topic,
                        Server(producer_name, producer_host, producer_port),
                        transaction_payload_size,
                    ),
                    transaction_data,
                )
            )
        # read payloads
        assert blog.get_size() == payload_size

        # cut offset
        if offset == 0:
            return blog

        return blog.cut(offset)


def crc32(data: bytes) -> int:
    """Compute CRC32 checksum of given bytes."""
    return zlib.crc32(data) & 0xFFFFFFFF


def read_bin(topic: str, offset: int = 0) -> BinLog:
    """Read bytes from the log file and convert it to DTO"""
    return BinLog.decode(read_bytes_or_create(get_topic_path(topic)), offset)


def append_bin(topic: str, data: TransactionLog):
    """Append transaction data and write"""
    binlog = read_bin(topic)
    binlog.append_atomic(data)


def append_bin_reserialize_all(topic: str, data: TransactionLog):
    """Append transaction data and write"""
    binlog = read_bin(topic)
    binlog.append(data)
    write_bytes(get_topic_path(topic), binlog.serialize_all())


def get_topic_path(topic: str, extension="blog"):
    """Helper function to get binlog file with topic name"""

    return os.path.join(
        Path(__file__).resolve().parents[1], "binlogs", topic, f"{topic}.{extension}"
    )


if __name__ == "__main__":

    append_bin(
        "test_topic",
        TransactionLog(
            TransactionLogHeader(
                1735123456, "test_topic", Server("Test_server", "localhost", 9000), 30
            ),
            os.urandom(30),
        ),
    )
    append_bin(
        "test_topic",
        TransactionLog(
            TransactionLogHeader(
                1735123456, "test_topic", Server("Test_server", "localhost", 9000), 30
            ),
            os.urandom(30),
        ),
    )
    append_bin(
        "test_topic",
        TransactionLog(
            TransactionLogHeader(
                1735123456, "test_topic", Server("Test_server", "localhost", 9000), 30
            ),
            os.urandom(30),
        ),
    )
    append_bin(
        "test_topic",
        TransactionLog(
            TransactionLogHeader(
                1735123456, "test_topic", Server("Test_server", "localhost", 9000), 30
            ),
            os.urandom(30),
        ),
    )

    result = read_bin("test_topic")
    print(vars(result))
