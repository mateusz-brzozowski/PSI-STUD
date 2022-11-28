# Laboratorium 1 Zadanie 1.2 Serwer w Pythonie
# Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk, Jakub Marcowski, Aleksandra Sypuła
# Data ukończenia: 27.11.2022

import socket
import sys
from typing import List, Tuple

# Klient wysyła a serwer odbiera datagramy o przyrastającej wielkości.
# Sprawdzić jaki był maksymalny rozmiar wysłanego (przyjętego) datagramu.
# Ustalić z dokładnością do jednego bajta jak duży datagram jest obsługiwany.

BUFSIZE = 100000  # max UDP datagram size is 65535 bytes


def parse_arguments(args: List[str]) -> Tuple[str, int]:
    if len(args) < 3:
        print('No host or port defined, using localhost at 8000 as default')
        host = '127.0.0.1'
        port = 8000
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    print(f'Will listen on {host}:{port}')

    return host, port


def bind_address(s: socket.socket, host: str, port: int) -> None:
    try:
        s.bind((host, port))
    except socket.error as exception:
        raise socket.error(
            f'Error while binding address to socket: {exception}'
        )


def work() -> bool:
    return True


def handle_received_datagram(s: socket.socket) -> None:
    try:
        (data, address) = s.recvfrom(BUFSIZE)

        print('Message received')
        print(f'Size of received data: {len(data)}')
        print(f'Client address: {address}')
    except socket.error as socketError:
        print(f'Error while receiving data: {socketError}')
    except UnicodeDecodeError as decodeError:
        print(f'Error while decoding received data: {decodeError}')


def prepare_socket_and_start_listening(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        bind_address(s, host, port)

        while work():
            handle_received_datagram(s)


def main(args: List[str]) -> None:

    try:
        (host, port) = parse_arguments(args)
    except ValueError as exception:
        print(f'Error while parsing arguments: {exception}')
        return

    try:
        prepare_socket_and_start_listening(host, port)
    except socket.error as exception:
        print(f'Caught exception: {exception}')


if __name__ == '__main__':
    main(sys.argv)
