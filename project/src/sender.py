from __future__ import annotations
from queue import Queue
from typing import Tuple, List, Optional, Type
from types import TracebackType
from packet import Packet
import socket
import diffie_hellman
import sys

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

    send_buffer: Queue[Data]
    receive_buffer: Queue[Data]
    _session_key: int
    _public_key: int            # A
    _private_key: int           # a
    _receiver_public_key: int   # B
    _prime_number: int          # p
    _primitive_root: int        # g
    _sock: socket.socket
    _type: int

    def __init__(self, address: Tuple[str, int]) -> None:
        (self._prime_number, self._primitive_root, self._private_key,
         self._public_key) = diffie_hellman.get_data()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._receiver_public_key = 1234    # TODO: get from receiver
        self._session_key = diffie_hellman.get_session_key(
            self._receiver_public_key, self._private_key, self._prime_number)

        encrypted_message = diffie_hellman.encrypt(
            'Hello world!', self._session_key)

        print(encrypted_message)

        print(diffie_hellman.decrypt(encrypted_message, self._session_key))

        try:
            self._sock.connect(address)
        except socket.error as exception:
            raise socket.error(
                f'Error while connecting: {exception}'
            )

        self._work = True

    def __enter__(self) -> Sender:
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self._sock.__exit__()

    def work(self) -> None:
        while self._work:
            if self.buffer_length() + 4 >= 512:
                self.send()
                self.handle_receive()
            pass
            # jeżeli buffer + potencjalna największa wiadomość >= 512 wyślij
            # czekaj na odpowiedź z timeoutem i jak się nie uda to retransmituj
            # jeśli się nie uda kilka razy to zakończ połączenie i ponowny connect

    def handle_receive(self) -> None:
        for _ in range(10):
            if self.receive():
                return
            else:
                self.send()
        # self.init() - wyślij initial packet 000

    def send(self) -> None:
        try:
            self._sock.send(buffer)
        except socket.error as exception:
            print(f'Exception while sending data: {exception}')
        except UnicodeEncodeError as exception:
            print(f'Exception while encoding text to bytes: {exception}')

    def receive(self) -> bool:
        try:    # jeśli otrzymam error inny niż malformed data zwracam true
            data = self._sock.recv(512)  # TODO: dodać timeout
            # czyścimy buffer ale tylko w odpowiednim przypadku
            print(data.decode('ascii'))
        except socket.error as exception:
            print(f'Exception while receiving data: {exception}')
        except UnicodeDecodeError as exception:
            print(f'Exception while decoding text to bytes: {exception}')

    def send_session_data(self) -> None:
        self._type = 1
        print(
            f"{self._type}:{self._public_key}:{self._primitive_root}:{self._prime_number}")
        message = f"{self._type:03b}{self._public_key:064b}{self._primitive_root:032b}{self._prime_number:032b}"
        print(message.encode())
        self.send(Packet(message.encode()))

    def send_declaration(self, content: bytes, stream_id: int) -> None:
        pass

    def send_data(self) -> None:
        # semafor na buforze
        pass


def generator(id, sender):
    pass
    # while true generuj dane sleep
    # timer, co 1 min dane
    # sender.send_data(data, id)


def parse_arguments(args: List[str]) -> Tuple[str, int, bool]:
    if len(args) < 3:
        print('No host and/or port defined, using localhost at 8080 as default')
        host = 'localhost'
        port = 8080
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    host_address = socket.gethostbyname(host)

    return host_address, port


def main(args: List[str]) -> None:
    try:
        (host, port) = parse_arguments(args)
    except socket.error as exception:
        print(f'Get host by name raised an exception: {exception}')
        return
    except ValueError as exception:
        print(f'Error while parsing arguments: {exception}')
        return

    with Sender((host, port)) as s:
        # inicjowanie generatorów i tu podaje s każdy na innym wątku
        try:
            s.work()
        except socket.error as exception:
            print(f'Caught exception: {exception}')

    print('Client finished.')


if __name__ == '__main__':
    main(sys.argv)
