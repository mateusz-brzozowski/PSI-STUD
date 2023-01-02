import sys
from typing import List, Optional

from database import Database
from packet import Packet


class SessionManager:
    """
    Zarządca sesji:
    - przechowuje informacje o aktywnej sesji
    - zachowuje informacje o stanie danego połączenia np.
        - adres IP oraz port klienta
        - id sesji
        - fazie sesji (nawiązywanie połączenia, uzgadnianie klucza,
        przesyłanie danych)
        - ustalony klucz sesyjny
        - ilość strumieni danych
    - obsługuje otrzymywane pakiety
    - uzgadnia klucz sesyjny
    - deszyfruje pakiety
    - decyduje czy dany pakiet ma sens w kontekście danej sesji
    - przygotowuje komunikaty (odpowiedzi) do przesłania do klienta
        - przekazuje je odbiorcy do wysłania
        - potwierdza wszystkie otrzymane poprawne pakiety
    - rozdziela poszczególne strumienie danych do odpowiednich miejsc
    w bazie danych
    """

    session_id: int
    session_key: str
    public_key: str
    private_key: str
    sender_public_key: str
    database: Database

    def __init__(self, host: str, port: int, database: Database) -> None:
        self.host = host
        self.port = port
        self.database = database

    def handle(self, packet: Packet) -> Optional[Packet]:
        packet_type = packet.content()[:3]
        print(f"Typ datagramu: {packet_type!r}")
        if packet_type == b"000":
            # potwierdzenie otwarcia sesji
            checksum = packet.content()[3:11]
            print("Otrzymano potwierdzenie otwarcia sesji")
            print(f"Suma kontrolna datagramu: {checksum!r}")
        elif packet_type == b"001":
            # uzgodnienie klucza symetrycznego
            checksum = packet.content()[3:19]
            server_public_key_B = packet.content()[19:83]
            print("Uzgodniono klucz sesyjny")
            print(f"Suma kontrolna datagramu: {checksum!r}")
            print(f"Klucz publiczny serwera (B): {server_public_key_B!r}")
        elif packet_type == b"010":
            # potwierdzenie odebrania informacji o sesji
            print("Potwierdzeno odebrania informacji o sesji")
            checksum = packet.content()[3:11]
            print("Otrzymano potwierdzenie otwarcia sesji")
            print(f"Suma kontrolna datagramu: {checksum!r}")
        elif packet_type == b"011":
            # potwierdzenie odbioru paczki danych
            print("Potwierdzono odbiór paczki danych")
            checksum = packet.content()[3:19]
            datagram_num = packet.content()[19:35]
            print("Otrzymano potwierdzenie otwarcia sesji")
            print(f"Suma kontrolna datagramu: {checksum!r}")
            print(f"Numer datagramu: {datagram_num!r}")
        elif packet_type == b"100":
            # przesłanie kodu błędu
            print("Przesłano kod błędu")
            checksum = packet.content()[3:11]
            print("Otrzymano potwierdzenie otwarcia sesji")
            print(f"Suma kontrolna datagramu: {checksum!r}")
        elif packet_type == b"101":
            # zamknięcie sesji
            print("Zamknięto sesję")
            checksum = packet.content()[3:11]
            print("Otrzymano potwierdzenie otwarcia sesji")
            print(f"Suma kontrolna datagramu: {checksum!r}")
        else:
            raise ValueError(f"Unrecognized packet: {packet_type!r}")
        print()
        return packet


def main(args: List[str]) -> None:
    session_manager = SessionManager("localhost", 8080)
    session_manager.handle(Packet(b"000" + b"11000110"))  # type, checksum
    session_manager.handle(
        Packet(
            b"001"  # type
            b"1010010101100010"  # checksum
            + b"1010010101100010"
            + b"1010010101100010"
            + b"1010010101100010"
            + b"1010010101100010"  # server's public key
        )
    )
    session_manager.handle(Packet(b"010" + b"10100100"))  # type, checksum
    session_manager.handle(
        Packet(
            b"011"  # type
            + b"1010010101100010"  # checksum
            + b"1010010101100010"  # datagram num
        )
    )
    session_manager.handle(Packet(b"100" + b"10100100"))  # type, checksum
    session_manager.handle(Packet(b"101" + b"10100100"))  # type, checksum


if __name__ == "__main__":
    main(sys.argv)
