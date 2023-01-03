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
    "initial": "000",
    "session_data": "001",
    "declaration": "010",
    "send": "011",
    "error": "100",
    "close": "101"
}

packet_type_server = {
    "initial": "000",
    "session_data": "001",
    "acknowledge": "010",
    "receive": "011",
    "terminal": "100",
    "close": "101",
    "malformed": "110",
}
