import sys
from typing import List, Optional

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
    # database: Database

    def __init__(self, host: str, port: int) -> None:
        pass

    def handle(self, packet: Packet) -> Optional[Packet]:
        return packet


def main(args: List[str]) -> None:
    pass


if __name__ == "__main__":
    main(sys.argv)
