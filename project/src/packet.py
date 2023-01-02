class Packet:
    _content: bytes
    # based on final implementation this might be just bytes
    # with special functions to convert it to more headers and data
    # or
    # it might be parsed to/from bytes to headers and data in a constructor

    def __init__(self, data: bytes) -> None:
        self._content: bytes = data

    def content(self) -> bytes:
        return self._content

    def size(self) -> int:
        return len(self._content)


packet_type_client = {
    "initial": b"000",
    "session_data": b"001",
    "declaration": b"010",
    "send": b"011",
    "error": b"100",
    "close": b"101"
}

packet_type_server = {
    "initial": b"000",
    "session_data": b"001",
    "acknowledge": b"010",
    "receive": b"011",
    "error": b"100",
    "close": b"101"
}
