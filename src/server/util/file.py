"""Typical file read/write utilities"""

from pathlib import Path
from server.system_logger import SLOG


def read_bytes_or_create(path: str) -> bytes:
    """Read"""
    p = Path(path)
    if not p.exists():
        p.write_bytes(b"")
        return b""
    return p.read_bytes()


def write_bytes(path: str, data: bytes) -> bool:
    """Write"""
    try:
        Path(path).write_bytes(data)
        return True
    except Exception as e:
        SLOG.error(e)
        return False


def append_bytes(path: str, data: bytes) -> None:
    """This won't be used since the header should be also updated when the payload has changed"""
    with open(path, "ab") as f:
        f.write(data)
