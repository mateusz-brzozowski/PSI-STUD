# Projekt
# Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk, Jakub Marcowski, Aleksandra Sypuła
# Data ukończenia: 16.01.2023

import struct
from datetime import datetime
from typing import Any, Optional


def datetime_to_bytes(datetime: datetime) -> bytes:
    return str.encode(bin(int(datetime.timestamp()))[2:])


def bytes_to_datetime(bytes: bytes) -> datetime:
    return datetime.fromtimestamp(int(bytes, 2))


def string_to_binary(string: str) -> str:
    return "".join(format(ord(i), "b") for i in string)


def pack(value: int, size: int) -> bytes:
    return struct.pack(f"{size}B", *value.to_bytes(size, "big"))


def unpack(value: bytes) -> int:
    return int.from_bytes(value, "big")


def suppress_warings(object: Any) -> Optional[Any]:
    """
    If you want to suppress warnings
    about unused variables, use this function.
    """
    return None if object is None else object
