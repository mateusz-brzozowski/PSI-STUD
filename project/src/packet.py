# Projekt - System niezawodnego strumieniowania danych po UDP
# Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk, Jakub Marcowski, Aleksandra Sypuła
# Data ukończenia: 16.01.2023

import diffie_hellman
from log_util import format_data


class Packet:
    _content: bytes

    def __init__(self, data: bytes) -> None:
        self._content: bytes = data

    def content(self) -> bytes:
        return self._content

    def size(self) -> int:
        return len(self._content)

    def msg_type(self) -> str:
        try:
            return self._content[:1].decode()
        except UnicodeDecodeError:
            print("Packet: Błąd w czasie dekodowania wartości polecenia")
            return "5"

    def encrypt(self, session_key: int) -> None:
        print(
            f"Packet: Wiadomość nie zakodowana: {format_data(self._content)}"
        )
        self._content = diffie_hellman.encrypt(self._content, session_key)
        print(f"Packet: Wiadomość zakodowana: {format_data(self._content)}")

    def decrypt(self, session_key: int) -> None:
        print(f"Packet: Zakodowana wiadomość: {format_data(self._content)}")
        self._content = diffie_hellman.decrypt(self._content, session_key)
        print(f"Packet: Odkodowana wiadomość: {format_data(self._content)}")


packet_type_client = {
    "initial": "1",
    "session_data": "2",
    "declaration": "3",
    "send": "4",
    "error": "5",
    "close": "6",
}

packet_type_server = {
    "initial": "1",
    "session_data": "2",
    "acknowledge": "3",
    "receive": "4",
    "terminal": "5",
    "close": "6",
}
