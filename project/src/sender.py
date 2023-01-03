from __future__ import annotations
from queue import Queue
from typing import Tuple, List, Optional, Type
from types import TracebackType
from packet import Packet, packet_type_client
from datetime import datetime
from threading import *
import time
import random
import string
import socket
import diffie_hellman
import sys
from utility import string_to_binary

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
    semaphore: Semaphore
    _session_key: int
    _public_key: int            # A
    _private_key: int           # a
    _receiver_public_key: int   # B
    _prime_number: int          # p
    _primitive_root: int        # g
    _sock: socket.socket
    _send_datagram_number: int
    _work: bool
    DATA_SIZE = 67
    MAX_DATA_SIZE = 512

    def __init__(self, address: Tuple[str, int], semaphore: Semaphore) -> None:
        (self._prime_number, self._primitive_root, self._private_key,
         self._public_key) = diffie_hellman.get_data()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._receiver_public_key = 1234    # TODO: get from receiver
        self._session_key = diffie_hellman.get_session_key(
            self._receiver_public_key, self._private_key, self._prime_number)
        self._send_datagram_number = 0
        self.semaphore = semaphore
        self.send_buffer = Queue()

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

        self.init()
        self._work = True  # TODO: jeżeli się zainicjuje to będzie true

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
            if self.buffer_length() + self.DATA_SIZE >= self.MAX_DATA_SIZE:
                self.send_data()
                self.handle_receive()

    def handle_receive(self) -> None:
        for _ in range(10):
            if self.receive():
                return
            else:
                self.send_data()
        self.init()

    def send(self, message: Packet) -> None:
        try:
            print(message.content())
            self._sock.send(message.content())
        except socket.error as exception:
            print(f'Exception while sending data: {exception}')
        except UnicodeEncodeError as exception:
            print(f'Exception while encoding text to bytes: {exception}')

    def receive(self) -> bool:
        try:    # TODO: jeśli otrzymam error inny niż malformed data zwracam true
            self._sock.settimeout(1)
            data = self._sock.recv(512)
            # print(data.decode('ascii'))
            # TODO: czyścimy buffer ale tylko w odpowiednim przypadku
        except socket.error as exception:
            print(f'Exception while receiving data: {exception}')
        except UnicodeDecodeError as exception:
            print(f'Exception while decoding text to bytes: {exception}')

    def init(self):
        self.send(Packet(packet_type_client["initial"].encode()))

    def send_session_data(self) -> None:
        self._type = 1
        print(
            f"{self._type}:{self._public_key}:{self._primitive_root}:{self._prime_number}")
        message = f"{self._type:03b}{self._public_key:064b}{self._primitive_root:032b}{self._prime_number:032b}"
        self.send(Packet(message.encode()))

    def send_declaration(self, content: bytes, stream_id: int) -> None:
        pass

    def send_data(self) -> None:
        message = packet_type_client["send"] + \
            f"{self._send_datagram_number:016b}"
        while not self.send_buffer.empty():
            data = self.send_buffer.get()
            message += f"{data.data_stream_id:03b}{int(data.time.timestamp()):032b}{string_to_binary(data.content).zfill(32)}"
        self.send(Packet(message.encode()))
        self._send_datagram_number += 1

    def save_data_to_buffer(self, data: Data) -> None:
        self.semaphore.acquire()
        self.send_buffer.put(data)
        self.semaphore.release()

    def buffer_length(self) -> int:
        return self.send_buffer.qsize() * self.DATA_SIZE + 3


def generate_data(length: int) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def thread_generator(id, sender):
    while True:
        sender.save_data_to_buffer(
            Data(id, datetime.now(), generate_data(4)))
        time.sleep(10)


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

    number_of_threads = 8
    threads = []
    semaphore = Semaphore(number_of_threads)

    with Sender((host, port), semaphore) as s:
        for thread_id in range(number_of_threads):
            threads.append(
                Thread(target=thread_generator, args=(thread_id, s)))
        for thread in threads:
            thread.start()

        try:
            s.work()
        except socket.error as exception:
            print(f'Caught exception: {exception}')

    print('Client finished.')


if __name__ == '__main__':
    main(sys.argv)
