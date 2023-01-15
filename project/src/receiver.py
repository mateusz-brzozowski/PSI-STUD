from __future__ import annotations

import socket
import sys
from importlib import util
from threading import Thread
from types import TracebackType
from typing import Dict, List, Optional, Tuple, Type

from database import Database
from packet import Packet
from session import SessionManager
from log_util import format_data


matplotlib_spec = util.find_spec("matplotlib")
if matplotlib_spec is not None:
    from interface import Interface


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
                f"Receiver: Wyjątek podczas bindowania adresu do gniazda: {exception}"
            ) from exception

    def receive_datagram(
        self,
    ) -> Tuple[Optional[Tuple[str, int]], Optional[Packet]]:
        try:
            (data, address) = self._sock.recvfrom(self.BUFSIZE)

            print(f"Receiver: Otrzymano wiadomość: {format_data(data)}")
            print(f"Receiver: Rozmiar otrzymanych danych: {len(data)}")
            print(f"Receiver: Adres klienta: {address}")

            return address, Packet(data)
        except socket.error as socketError:
            print(
                f"Receiver: Wyjątek podczas otrzymywania danych: {socketError}")
        except UnicodeDecodeError as decodeError:
            print(
                f"Receiver: Wyjątek podczas dekodowania otrzymanych danych: {decodeError}"
            )

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
        except socket.error as exception:
            print(f"Receiver: Wyjątek podczas obsługi danych: {exception}")

        return None

    def send_datagram(
        self, address: Tuple[str, int], datagram: Packet
    ) -> None:
        try:
            self._sock.sendto(datagram.content(), address)
            # ignore case not enough bytes sent -> due to invalid packet
            # received client will resend his packet and then the server
            # will respond again
            print(
                f"Receiver: Wiadomość wysłana: {format_data(datagram.content())}"
            )
        except socket.error as socketError:
            print(f"Receiver: Wyjątek podczas wysyłania danych: {socketError}")


def parse_arguments(args: List[str]) -> Tuple[str, int]:
    if len(args) < 3:
        print(
            "Brak zdefiniowanego hosta lub portu, "
            "jako wartość domyślna użyty zostanie adres 0.0.0.0 na porcie 8080"
        )
        host = "0.0.0.0"
        port = 8080
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    return host, port


def thread_test(database: Database, host: str, port: int) -> None:
    with Receiver(database) as r:
        try:
            r.listen(host, port)
        except socket.error as exception:
            print(f"Receiver: Złapano wyjątek: {exception}")
            return


def main(args: List[str]) -> None:
    try:
        (host, port) = parse_arguments(args)
    except ValueError as exception:
        print(f"Wyjątek podczas parsowania argumentów: {exception}")
        return

    database = Database()
    thread_test_isnt = Thread(target=thread_test, args=(database, host, port))
    thread_test_isnt.start()
    if matplotlib_spec:
        interface_inst = Interface(database)
        interface_inst.show()
    else:
        print("Nie można wyświetlić interfejsu graficznego "
              "- brak biblioteki matplotlib")


if __name__ == "__main__":
    main(sys.argv)
