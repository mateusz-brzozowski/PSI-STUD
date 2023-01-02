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

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port

    def handle(self, packet: Packet) -> Optional[Packet]:
        packet_type = packet.content()[:3]
        print(f"Typ datagramu: {packet_type}")
        if packet_type == b"000":
            # potwierdzenie otwarcia sesji
            control_sum = packet.content()[3:11]
            print("Otrzymano potwierdzenie otwarcia sesji")
            print(f"Suma kontrolna datagramu: {control_sum}")
        elif packet_type == b"001":
            # uzgodnienie klucza symetrycznego
            control_sum = packet.content()[3:19]
            server_public_key_B = packet.content()[19:83]
            print("Uzgodniono klucz sesyjny")
            print(f"Suma kontrolna datagramu: {control_sum}")
            print(f"Klucz publiczny serwera (B): {server_public_key_B}")
        elif packet_type == b"010":
            # potwierdzenie odebrania informacji o sesji
            print("Potwierdzeno odebrania informacji o sesji")
            control_sum = packet.content()[3:11]
            print("Otrzymano potwierdzenie otwarcia sesji")
            print(f"Suma kontrolna datagramu: {control_sum}")
        elif packet_type == b"011":
            # potwierdzenie odbioru paczki danych
            print("Potwierdzono odbiór paczki danych")
            control_sum = packet.content()[3:19]
            datagram_num = packet.content()[19:35]
            print("Otrzymano potwierdzenie otwarcia sesji")
            print(f"Suma kontrolna datagramu: {control_sum}")
            print(f"Numer datagramu: {datagram_num}")
        elif packet_type == b"100":
            # przesłanie kodu błędu
            print("Przesłano kod błędu")
            control_sum = packet.content()[3:11]
            print("Otrzymano potwierdzenie otwarcia sesji")
            print(f"Suma kontrolna datagramu: {control_sum}")
        elif packet_type == b"101":
            # zamknięcie sesji
            print("Zamknięto sesję")
            control_sum = packet.content()[3:11]
            print("Otrzymano potwierdzenie otwarcia sesji")
            print(f"Suma kontrolna datagramu: {control_sum}")
        print()
        return packet


def main(args: List[str]) -> None:
    session_manager = SessionManager("localhost", 8080)
    session_manager.handle(Packet(b"000" +  # type
                                  b"19347123"))  # control sum
    session_manager.handle(Packet(b"00111890401" +  # type
                                  b"17897471" +  # control sum
                                  b"9847103480157269" +
                                  b"8023475892758123" +
                                  b"0847138540615771" +
                                  b"0985624780650914"))  # server's public key
    session_manager.handle(Packet(b"010" +  # type
                                  b"18501891"))  # control sum
    session_manager.handle(Packet(b"011" +  # type
                                  b"1789419319084104" +  # control sum
                                  b"2357247346783582"))  # datagram num
    session_manager.handle(Packet(b"100" +  # type
                                  b"18390481"))  # control sum
    session_manager.handle(Packet(b"101" +  # type
                                  b"81947814"))  # control sum


if __name__ == "__main__":
    main(sys.argv)
