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

import diffie_hellman
from data import Data
from log_util import format_data
from packet import Packet, packet_type_client, packet_type_server
from utility import pack, unpack

SENDER_STATES = {
    "INIT": 1,
    "SYMMETRIC_KEY_NEGOTIATION": 2,
    "SESSION_CONFIRMATION": 3,
    "DATA_TRANSFER": 4,
    "SESSION_CLOSING": 5
}

SEND_DATA_MAX_INTERVAL = 30


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

    _state: int
    send_buffer: Queue[Data]
    write_semaphore: Semaphore
    _read_semaphore: Semaphore
    _session_key: Optional[int]
    _public_key: int  # A
    _private_key: int  # a
    _receiver_public_key: int  # B
    _prime_number: int  # p
    _primitive_root: int  # g
    _sock: socket.socket
    _send_datagram_number: int
    _work: bool
    _previous_datagram: Packet
    _previous_message_content: Optional[bytes]
    _stream_ids: List[str] = []
    DATA_SIZE = 9
    MAX_DATA_SIZE = 512

    def __init__(self, address: Tuple[str, int], write_semaphore: Semaphore, stream_ids: List[str], bind_port: Optional[int]) -> None:
        (self._prime_number, self._primitive_root, self._private_key,
         self._public_key) = diffie_hellman.get_data()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._send_datagram_number = 0
        self.write_semaphore = write_semaphore
        self._read_semaphore = Semaphore(1)
        self._read_semaphore.acquire()
        self.send_buffer = Queue()
        self._sock.settimeout(10)
        self._state = SENDER_STATES["INIT"]
        self._work = True
        self._previous_message_content = None
        self._stream_ids = stream_ids

        try:
            if bind_port:
                self._sock.bind(("0.0.0.0", bind_port))
            self._sock.connect(address)
        except socket.error as exception:
            raise socket.error(
                f"Sender: Wyjątek podczas nawiązywania połączenia: {exception}"
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

    def work(self) -> None:
        while self._work:
            print(f"Sender: Aktualny stan: {self._state}")

            if self._state == SENDER_STATES["INIT"]:
                self.init()
            elif self._state == SENDER_STATES["SYMMETRIC_KEY_NEGOTIATION"]:
                self.send_session_data()
            elif self._state == SENDER_STATES["SESSION_CONFIRMATION"]:
                self.send_declaration()
            elif self._state == SENDER_STATES["DATA_TRANSFER"]:
                if self._previous_message_content:
                    self.send_data(Packet(
                        packet_type_client["send"].encode()
                        + pack(self._send_datagram_number, 2)
                        + self._previous_message_content
                    ))
                else:
                    self.send_new_data()
            elif self._state == SENDER_STATES["SESSION_CLOSING"]:
                self.send_close_session()

    def switch(self) -> None:
        self._work = not self._work

    def send(self, message: Packet) -> None:
        self._previous_datagram = Packet(message.content()[:])

        if self._session_key:
            message.encrypt(self._session_key)

        try:
            self._sock.send(message.content())
            print(
                f"Sender: Wysłana wiadomość: {format_data(message.content())}"
            )
        except socket.error as exception:
            print(f"Sender: Wyjątek podczas wysyłania danych: {exception}")
        except UnicodeEncodeError as exception:
            print(
                f"Sender: Wyjątek podczas enkodowania tekstu na bajty: {exception}")

    def receive(self) -> Optional[Packet]:
        try:
            data = self._sock.recv(512)

            print(f"Sender: Otrzymana wiadomość: {data}")

            datagram = Packet(data)

            if self._session_key:
                datagram.decrypt(self._session_key)

            return datagram

        except socket.error as exception:
            print(f"Sender: Wyjątek podczas otrzymywania danych:: {exception}")
        except UnicodeDecodeError as exception:
            print(
                f"Sender: Wyjątek podczas dekodowania tekstu na bajty: {exception}")

        return None

    def handle_receive(self) -> Optional[Packet]:
        for _ in range(10):
            datagram = self.receive()

            if datagram:
                return datagram
            else:
                self.send(self._previous_datagram)

        self._state = SENDER_STATES["SESSION_CLOSING"]
        return None

    def init(self):
        self._session_key = None
        self._send_datagram_number = 0

        message = Packet(packet_type_client["initial"].encode())

        self.send(message)

        received = self.handle_receive()

        if received:
            data = received.content()
            if len(data) >= 1 and received.msg_type() == packet_type_server["initial"]:
                self._state = SENDER_STATES["SYMMETRIC_KEY_NEGOTIATION"]
            else:
                self._state = SENDER_STATES["SESSION_CLOSING"]
        else:
            self._work = False

    def send_session_data(self) -> None:
        content = packet_type_client["session_data"].encode() \
            + pack(self._public_key, 8) \
            + pack(self._primitive_root, 4) \
            + pack(self._prime_number, 8)

        message = Packet(content)

        self.send(message)

        received = self.handle_receive()

        if received:
            data = received.content()
            if len(data) >= 9 and received.msg_type() == packet_type_server["session_data"]:
                self._receiver_public_key = unpack(data[1:9])
                self._session_key = diffie_hellman.get_session_key(
                    self._receiver_public_key, self._private_key, self._prime_number
                )
                self._state = SENDER_STATES["SESSION_CONFIRMATION"]
            else:
                self._state = SENDER_STATES["SESSION_CLOSING"]
        else:
            self._state = SENDER_STATES["SESSION_CLOSING"]

    def send_declaration(self) -> None:
        content = packet_type_client["declaration"].encode() \
            + pack(len(self._stream_ids), 1)

        for stream in self._stream_ids:
            content += stream.ljust(16).encode()

        message = Packet(content)
        self.send(message)

        received = self.handle_receive()

        if received:
            data = received.content()
            if len(data) >= 1 and received.msg_type() == packet_type_server["acknowledge"]:
                self._state = SENDER_STATES["DATA_TRANSFER"]
            else:
                self._state = SENDER_STATES["SESSION_CLOSING"]
        else:
            self._state = SENDER_STATES["SESSION_CLOSING"]

    def send_new_data(self) -> None:
        message = self.prepare_next_packet()
        self._previous_message_content = message.content()[3:]
        self.send_data(message)

    def send_data(self, message: Packet) -> None:
        self.send(message)

        received = self.handle_receive()

        if received:
            data = received.content()

            number = -1
            if len(data) >= 3:
                number = unpack(data[1:3])

            if received.msg_type() == packet_type_server["receive"] and self._send_datagram_number == number:
                self._send_datagram_number = \
                    (self._send_datagram_number + 1) % 2 ** 16
                self._previous_message_content = None
                self._state = SENDER_STATES["DATA_TRANSFER"]
            elif received.msg_type() == packet_type_server["receive"]:
                self._state = SENDER_STATES["DATA_TRANSFER"]
            else:
                self._state = SENDER_STATES["SESSION_CLOSING"]
        else:
            self._state = SENDER_STATES["SESSION_CLOSING"]

    def send_close_session(self) -> None:
        content = packet_type_client["close"].encode()
        message = Packet(content)
        self.send(message)

        received = self.handle_receive()

        if received:
            data = received.content()
            if len(data) >= 1 and received.msg_type() == packet_type_server["close"]:
                self._state = SENDER_STATES["INIT"]
            else:
                self._state = SENDER_STATES["INIT"]
        else:
            self._state = SENDER_STATES["INIT"]

    def save_data_to_buffer(self, data: Data) -> None:
        self.write_semaphore.acquire()

        self.send_buffer.put(data)

        if self.is_buffer_ready_to_read():
            self._read_semaphore.release()

        self.write_semaphore.release()

    def prepare_next_packet(self) -> Packet:
        self._read_semaphore.acquire(
            timeout=SEND_DATA_MAX_INTERVAL
        )

        content = packet_type_client["send"].encode() \
            + pack(self._send_datagram_number, 2)

        for _ in range((self.MAX_DATA_SIZE - len(content)) // self.DATA_SIZE):
            if self.send_buffer.empty():
                break

            data = self.send_buffer.get()
            content += pack(self._stream_ids.index(data.data_stream_id), 1)
            content += pack(int(data.time.timestamp()), 4)
            content += data.content

        if self.is_buffer_ready_to_read():
            self._read_semaphore.release()

        return Packet(content)

    def is_buffer_ready_to_read(self) -> bool:
        return self.send_buffer.qsize() * self.DATA_SIZE + 3 > self.MAX_DATA_SIZE


def generate_data(length: int) -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def thread_generator(id: str, sender: Sender) -> None:
    last = random.randint(100, 1000)
    while True:
        new = min(max(last + random.randint(-50, 50), 100), 1000)
        last = new
        sender.save_data_to_buffer(
            Data(id, datetime.now(), pack(new, 4))
        )
        time.sleep(random.random() + 1.1)


def parse_arguments(args: List[str]) -> Tuple[str, int, Optional[int]]:
    if len(args) < 3:
        print(
            "Brak zdefiniowanego hosta lub portu, "
            "jako wartość domyślna użyty zostanie "
            "adres localhost na porcie 8080"
        )
        host = "localhost"
        port = 8080
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    bind_port = None
    if (len(args) == 4):
        bind_port = int(sys.argv[3])

    host_address = socket.gethostbyname(host)

    return host_address, port, bind_port


THREAD_IDS = [
    "Miernik CO2",
    "Miernik SO2",
    "Miernik NO2",
    "Miernik CO",
    "Miernik C6H6",
    "Miernik O3",
    "Miernik PM10",
    "Miernik PM2.5"
]


def main(args: List[str]) -> None:
    try:
        (host, port, bind_port) = parse_arguments(args)
    except socket.error as exception:
        print(f"Metoda gethostbyname() zgłosiła wyjątek: {exception}")
        return
    except ValueError as exception:
        print(f"Wyjątek podczas parsowania argumentów: {exception}")
        return

    number_of_threads = 8
    threads: List[Thread] = []
    write_semaphore = Semaphore(number_of_threads)

    with Sender((host, port), write_semaphore, THREAD_IDS, bind_port) as s:
        threads.extend(
            Thread(target=thread_generator, args=(THREAD_IDS[thread_num], s))
            for thread_num in range(number_of_threads)
        )
        for thread in threads:
            thread.start()

        try:
            s.work()
        except socket.error as exception:
            print(f"Sender: Złapano wyjątek: {exception}")

    print("Klient zakończył swoje działanie")


if __name__ == "__main__":
    main(sys.argv)
