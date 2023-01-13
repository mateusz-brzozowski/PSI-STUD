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
from data import SenderData
from packet import Packet, packet_type_client, packet_type_server
from utility import pack, unpack


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
        (self._prime_number, self._primitive_root, self._private_key,
         self._public_key) = diffie_hellman.get_data()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._send_datagram_number = 0
        self.semaphore = semaphore
        self.send_buffer = Queue()
        self._sock.settimeout(10)
        self._session_key = None

        try:
            self._sock.connect(address)
        except socket.error as exception:
            raise socket.error(
                f"Wyjątek podczas nawiązywania połączenia: {exception}"
            ) from exception

        self.init()
        self.send_session_data()
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
            if chr(message.content()[0]) == packet_type_client["declaration"]:
                msg = message.content().decode()
                msg_type = int(msg[0])
                msg_sen_num = int(msg[1])
                data_str = "".join(
                    f"[{msg[i:i + 16]}]" for i in range(2, len(msg), 16)
                )
                print(
                    f'Wiadomość wysłana: "{msg_type} {msg_sen_num} {data_str}"'
                )
            elif chr(message.content()[0]) == packet_type_client["initial"]:
                print(f"Wiadomość wysłana: {message.content().decode()}")
            else:
                self._extracted_from_send_14(message)

            if self._session_key:
                encrypted_message = diffie_hellman.encrypt(
                    message.content(), self._session_key)
                self._sock.send(encrypted_message)
            else:
                self._sock.send(message.content())

            self._previous_datagram = message
        except socket.error as exception:
            print(f"Wyjątek podczas wysyłania danych: {exception}")
        except UnicodeEncodeError as exception:
            print(f"Wyjątek podczas enkodowania tekstu na bajty: {exception}")

    # TODO Rename this here and in `send`
    def _extracted_from_send_14(self, message: Packet) -> None:
        msg_type = int(chr(message.content()[0]))
        datagram_num = unpack(message.content()[1:3])
        data_str: str = ""
        for i in range(3, len(message.content()), self.DATA_SIZE):
            data_id = unpack(message.content()[i: i + 1])
            data_timestamp = unpack(message.content()[i + 1: i + 5])
            data_content = unpack(
                message.content()[i + 5: i + self.DATA_SIZE]
            )
            data_str += f"[{data_id} {data_timestamp} {data_content}]"
        print("Wiadomość wysłana: " f'{msg_type} {datagram_num} {data_str}"')
        print("Wiadomość wysłana (raw): " f'{message.content()[:100]!r}[...]"')

    def receive(self) -> bool:
        try:  # TODO: jeśli otrzymam error inny niż malformed data zwracam true
            data = self._sock.recv(512)
            msg_type = chr(data[0])
            if msg_type == packet_type_server['receive']:
                msg_content = unpack(data[1:])
                print(f"Otrzymana wiadomość: {msg_type} {msg_content}")
            elif msg_type == packet_type_server["session_data"]:
                self._receiver_public_key = unpack(data[1:9])
                self._session_key = diffie_hellman.get_session_key(
                    self._receiver_public_key, self._private_key, self._prime_number)
            else:
                print(f"Otrzymana wiadomość: {data.decode()}")

            if self._previous_datagram.content()[:1] == data[:1]:
                return True
            # print(data.decode('ascii'))
            # TODO: czyścimy buffer ale tylko w odpowiednim przypadku
        except socket.error as exception:
            print(f"Wyjątek podczas otrzymywania danych:: {exception}")
        except UnicodeDecodeError as exception:
            print(f"Wyjątek podczas dekodowania tekstu na bajty: {exception}")
        return False

    def init(self):
        self.send(Packet(packet_type_client["initial"].encode()))
        self.handle_receive()

    def send_session_data(self) -> None:
        message = packet_type_client["session_data"].encode(
        ) + pack(self._public_key, 8) + pack(self._primitive_root, 4) + pack(self._prime_number, 4)
        self.send(Packet(message))
        self.handle_receive()

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
        # while not self.send_buffer.empty():
        for _ in range((self.MAX_DATA_SIZE - len(message)) // self.DATA_SIZE):
            data = self.send_buffer.get()
            message += pack(data.data_stream_id, 1)
            message += pack(int(data.time.timestamp()), 4)
            message += data.content

        print(f"Rozmiar pakietu: {len(message)}")
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
    last = random.randint(100, 1000)
    while True:
        new = min(max(last + random.randint(-50, 50), 100), 1000)
        last = new
        sender.save_data_to_buffer(
            SenderData(id, datetime.now(), pack(new, 4))
        )
        time.sleep(random.random() + 1.1)


def parse_arguments(args: List[str]) -> Tuple[str, int]:
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

    host_address = socket.gethostbyname(host)

    return host_address, port


def main(args: List[str]) -> None:
    try:
        (host, port) = parse_arguments(args)
    except socket.error as exception:
        print(f"Metoda gethostbyname() zgłosiła wyjątek: {exception}")
        return
    except ValueError as exception:
        print(f"Wyjątek podczas parsowania argumentów: {exception}")
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
            print(f"Złapano wyjątek: {exception}")

    print("Klient zakończył swoje działanie")


if __name__ == "__main__":
    main(sys.argv)
