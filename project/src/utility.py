from datetime import datetime


def datetime_to_bytes(datetime: datetime) -> bytes:
    return str.encode(bin(int(datetime.timestamp()))[2:])


def bytes_to_datetime(bytes: bytes) -> datetime:
    return datetime.fromtimestamp(int(bytes, 2))


def string_to_binary(string: str) -> str:
    return ''.join(format(ord(i), 'b') for i in string)
