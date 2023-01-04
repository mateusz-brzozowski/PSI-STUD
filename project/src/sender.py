from __future__ import annotations

import random
import socket
import string
import sys
import time
from datetime import datetime
from queue import Queue
from threading import Semaphore, Thread
from types import TracebackType
from typing import List, Optional, Tuple, Type

# import diffie_hellman
from data import SenderData
from packet import Packet, packet_type_client
from utility import pack


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

    send_buffer: Queue[SenderData]
    semaphore: Semaphore
    _session_key: int
    _public_key: int  # A
    _private_key: int  # a
    _receiver_public_key: int  # B
    _prime_number: int  # p
    _primitive_root: int  # g
    _sock: socket.socket
    _send_datagram_number: int
    _work: bool
    _previous_datagram: Packet
    DATA_SIZE = 9
    MAX_DATA_SIZE = 512
    threads = {
        0: "Miernik CO2",
        1: "Miernik SO2",
        2: "Miernik NO2",
        3: "Miernik CO",
        4: "Miernik C6H6",
        5: "Miernik O3",
        6: "Miernik PM10",
        7: "Miernik PM2.5",
    }

    def __init__(self, address: Tuple[str, int], semaphore: Semaphore) -> None:
        # (self._prime_number, self._primitive_root, self._private_key,
        #  self._public_key) = diffie_hellman.get_data()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self._receiver_public_key = 1234    # TODO: get from receiver
        # self._session_key = diffie_hellman.get_session_key(
        #     self._receiver_public_key, self._private_key, self._prime_number)
        self._send_datagram_number = 0
        self.semaphore = semaphore
        self.send_buffer = Queue()
        self._sock.settimeout(10)

        # encrypted_message = diffie_hellman.encrypt(
        #     'Hello world!', self._session_key)

        # print(encrypted_message)

        # print(diffie_hellman.decrypt(encrypted_message, self._session_key))

        try:
            self._sock.connect(address)
        except socket.error as exception:
            raise socket.error(
                f"Error while connecting: {exception}"
            ) from exception

        self.init()
        self.send_declaration()

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
            if 3 + self.buffer_length() + self.DATA_SIZE >= self.MAX_DATA_SIZE:
                self.send_data()
                self.handle_receive()

    def handle_receive(self) -> bool:
        for _ in range(10):
            if self.receive():
                return True
            else:
                self.send(self._previous_datagram)
        self.init()
        return False

    def send(self, message: Packet) -> None:
        try:
            print(f"message send: {message.content()!r}")
            self._sock.send(message.content())
            self._previous_datagram = message
        except socket.error as exception:
            print(f"Exception while sending data: {exception}")
        except UnicodeEncodeError as exception:
            print(f"Exception while encoding text to bytes: {exception}")

    def receive(self) -> bool:
        try:  # TODO: jeśli otrzymam error inny niż malformed data zwracam true
            data = self._sock.recv(512)
            print(f"message received: {data!r}")
            if self._previous_datagram.content()[:1] == data[:1]:
                return True
            # print(data.decode('ascii'))
            # TODO: czyścimy buffer ale tylko w odpowiednim przypadku
        except socket.error as exception:
            print(f"Exception while receiving data: {exception}")
        except UnicodeDecodeError as exception:
            print(f"Exception while decoding text to bytes: {exception}")
        return False

    def init(self):
        self.send(Packet(packet_type_client["initial"].encode()))
        self.handle_receive()

    def send_session_data(self) -> None:
        self._type = 1
        print(
            f"{self._type}:{self._public_key}:"
            f"{self._primitive_root}:{self._prime_number}"
        )
        message = (
            f"{self._type:03b}{self._public_key:064b}"
            f"{self._primitive_root:032b}{self._prime_number:032b}"
        )
        self.send(Packet(message.encode()))

    def send_declaration(self) -> None:
        message = packet_type_client["declaration"] + str(len(self.threads))
        for thread in self.threads.values():
            message += thread.ljust(16)
        self.send(Packet(message.encode()))
        if self.handle_receive():
            self._work = True

    def send_data(self) -> None:
        message = packet_type_client["send"].encode() + pack(
            self._send_datagram_number, 2
        )
        while not self.send_buffer.empty():
            data = self.send_buffer.get()
            message += pack(data.data_stream_id, 1)
            message += pack(int(data.time.timestamp()), 4)
            message += data.content

        self.send(Packet(message))
        self._send_datagram_number += 1

    def save_data_to_buffer(self, data: SenderData) -> None:
        self.semaphore.acquire()
        self.send_buffer.put(data)
        self.semaphore.release()

    def buffer_length(self) -> int:
        return self.send_buffer.qsize() * self.DATA_SIZE + 3


def generate_data(length: int) -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def thread_generator(id: int, sender: Sender) -> None:
    while True:
        sender.save_data_to_buffer(
            SenderData(id, datetime.now(), pack(random.randint(100, 1000), 4))
        )
        time.sleep(random.randint(1, 10) / 10)


def parse_arguments(args: List[str]) -> Tuple[str, int]:
    if len(args) < 3:
        print(
            "No host and/or port defined, using localhost at 8080 as default"
        )
        host = "localhost"
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
        print(f"Get host by name raised an exception: {exception}")
        return
    except ValueError as exception:
        print(f"Error while parsing arguments: {exception}")
        return

    number_of_threads = 8
    threads: List[Thread] = []
    semaphore = Semaphore(number_of_threads)

    with Sender((host, port), semaphore) as s:
        threads.extend(
            Thread(target=thread_generator, args=(thread_id, s))
            for thread_id in range(number_of_threads)
        )
        for thread in threads:
            thread.start()

        try:
            s.work()
        except socket.error as exception:
            print(f"Caught exception: {exception}")

    print("Client finished.")


if __name__ == "__main__":
    main(sys.argv)
