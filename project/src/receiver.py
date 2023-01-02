from __future__ import annotations

import socket
import sys
from types import TracebackType
from typing import Dict, List, Optional, Tuple, Type

from packet import Packet
from session import SessionManager
from database import Database


class Receiver:
    """
    Odbiorca komunikatów:
    - odbiera poszczególne komunikaty
    - sprawdza czy dane z nagłówka są poprawne
    - rozpoznaje numer sesji na podstawie nagłówka
        - w przypadku nieznanego numeru sesji tworzy nowego zarządce sesji
    - przekazuje pakiet do obsługi przez odpowiedniego zarządcę sesji
    - przekazuje komunikaty wygenerowane przez zarządcę sesji
      do odpowiedniego klienta
    """

    BUFSIZE = 512
    _session_managers: Dict[str, SessionManager] = {}
    _sock: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _work: bool = True
    _database: Database

    def __init__(self, database: Database) -> None:
        self._database = database

    def __enter__(self) -> Receiver:
        return self

    def __exit__(
        self,
        exception_type: Optional[Type[BaseException]],
        exception_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self._sock.__exit__()

    def switch(self) -> None:
        self._work = not self._work

    def listen(self, host: str = "0.0.0.0", port: int = 8080):
        self.bind_address(host, port)

        while self._work:
            address, datagram = self.receive_datagram()

            if address and datagram:
                if datagram := self.handle(address, datagram):
                    self.send_datagram(address, datagram)

    def bind_address(self, host: str, port: int) -> None:
        try:
            self._sock.bind((host, port))
        except socket.error as exception:
            raise socket.error(
                f"Error while binding address to socket: {exception}"
            ) from exception

    def receive_datagram(
        self,
    ) -> Tuple[Optional[Tuple[str, int]], Optional[Packet]]:
        try:
            (data, address) = self._sock.recvfrom(self.BUFSIZE)

            print("Message received")
            print(f"Size of received data: {len(data)}")
            print(f"Client address: {address}")

            return address, Packet(data)
        except socket.error as socketError:
            print(f"Error while receiving data: {socketError}")
        except UnicodeDecodeError as decodeError:
            print(f"Error while decoding received data: {decodeError}")

        return None, None

    def handle(
        self, address: Tuple[str, int], datagram: Packet
    ) -> Optional[Packet]:
        session_key = f"{address[0]}:{address[1]}"
        if session_key not in self._session_managers.keys():
            self._session_managers[session_key] = SessionManager(
                address[0], address[1], self._database
            )

        manager = self._session_managers[session_key]

        try:
            return manager.handle(datagram)
        except Exception as exception:
            print(exception)

        return None

    def send_datagram(
        self, address: Tuple[str, int], datagram: Packet
    ) -> None:
        try:
            self._sock.sendto(datagram.content(), address)
            # ignore case not enough bytes sent -> due to invalid packet
            # received client will resend his packet and then the server
            # will respond again
            print("Message sent")
        except socket.error as socketError:
            print(f"Error while sending data: {socketError}")


def parse_arguments(args: List[str]) -> Tuple[str, int]:
    if len(args) < 3:
        print("No host or port defined, using localhost at 8080 as default")
        host = "0.0.0.0"
        port = 8080
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    return host, port


def main(args: List[str]) -> None:
    try:
        (host, port) = parse_arguments(args)
    except ValueError as exception:
        print(f"Error while parsing arguments: {exception}")
        return

    database = Database()

    with Receiver(database) as r:
        try:
            r.listen(host, port)
        except socket.error as exception:
            print(f"Caught exception: {exception}")
            return


if __name__ == "__main__":
    main(sys.argv)
