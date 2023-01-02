from queue import Queue
from typing import Tuple

from data import Data


class Sender:
    """
    Nadawca komunikatów:
    - inicjuje sesję z serwerem
    - negocjuje klucz sesyjny z serwerem
    - buforuje otrzymywane dane do osiągnięcia limitu wielkości
      wysyłanego pakietu - 512 B
    - zapisuje pochodzenie danych z poszczególnych wątków
    - zapisuje czas otrzymania danych ze strumienia
    - szyfruje dane ustalonym kluczem sesyjnym
    - działa w trybie prześlij pakiet i czekaj na odpowiedź
      (z ustawionym timeout)
        - po czasie bez odpowiedzi - retransmituje ponownie pakiet
        - gdy kilka razy będzie następowała retransmisja i dalej
          nie otrzyma odpowiedzi - kończy połączenie
    """

    buffer: Queue[Data]
    session_key: str
    public_key: str
    private_key: str
    receiver_public_key: str

    def __init__(self, address: Tuple[str, int]) -> None:
        pass

    def send(self, content: bytes, stream_id: int) -> None:
        pass
