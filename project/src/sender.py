from __future__ import annotations

import socket
import sys
from queue import Queue
from types import TracebackType
from typing import List, Optional, Tuple, Type

import diffie_hellman
from data import Data
from packet import Packet


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
    _session_key: int
    _public_key: int  # A
    _private_key: int  # a
    _receiver_public_key: int  # B
    _prime_number: int  # p
    _primitive_root: int  # g
    _sock: socket.socket
    _type: int

    def __init__(self, address: Tuple[str, int]) -> None:
        (
            self._prime_number,
            self._primitive_root,
            self._private_key,
            self._public_key,
        ) = diffie_hellman.get_data()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._receiver_public_key = 1234  # TODO: get from receiver
        self._session_key = diffie_hellman.get_session_key(
            self._receiver_public_key, self._private_key, self._prime_number
        )

        encrypted_message = diffie_hellman.encrypt(
            "Hello world!", self._session_key
        )

        print(encrypted_message)

        print(diffie_hellman.decrypt(encrypted_message, self._session_key))

        try:
            self._sock.connect(address)
        except socket.error as exception:
            raise socket.error(
                f"Error while connecting: {exception}"
            ) from exception

    def __enter__(self) -> Sender:
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self._sock.__exit__()

    def send(self, datagram: Packet) -> None:
        try:
            self._sock.send(datagram)
        except socket.error as exception:
            print(f"Exception while sending data: {exception}")
        except UnicodeEncodeError as exception:
            print(f"Exception while encoding text to bytes: {exception}")

    def send_session_data(self) -> None:
        self._type = 1
        control_sum = (
            self._public_key
            + self._primitive_root
            + self._prime_number % 2**16
        )
        print(
            f"{self._type}:{control_sum}:{self._public_key}:{self._primitive_root}:{self._prime_number}"
        )
        print(
            f"{self._type:03b}{control_sum:016b}{self._public_key:064b}{self._primitive_root:032b}{self._prime_number:032b}"
        )

    def send_declaration(self, content: bytes, stream_id: int) -> None:
        pass

    def send_data(self) -> None:
        pass


def parse_arguments(args: List[str]) -> Tuple[str, int]:
    if len(args) < 3:
        print(
            "No host and/or port defined, using localhost at 8080 as default"
        )
        host = "localhost"
        port = 8000
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    host_address = socket.gethostbyname(host)

    return host_address, port


def main(args: List[str]) -> None:
    try:
        (host, port) = parse_arguments(args)
    except socket.error as exception:
        print(f"Get host by name raised an exception: {exception}")
        return
    except ValueError as exception:
        print(f"Error while parsing arguments: {exception}")
        return

    with Sender((host, port)) as s:
        try:
            s.send()
        except socket.error as exception:
            print(f"Caught exception: {exception}")

    print("Client finished.")


if __name__ == "__main__":
    main(sys.argv)
