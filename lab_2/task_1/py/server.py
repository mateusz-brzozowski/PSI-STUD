# Laboratorium 1 Zadanie 1.1 Serwer w Pythonie
# Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk, Jakub Marcowski, Aleksandra Sypuła
# Data ukończenia: 27.11.2022

import socket
import sys
from typing import List, Tuple

# Klient wysyła a serwer odbiera porcje danych o stałym, niewielkim rozmiarze (rzędu kilkudziesięciu bajtów).
# Mogą one zawierać ustalony „na sztywno” lub generowany napis – np. „abcde….”, „bcdef…​”, itd.
# Po wysłaniu danych klient powinien kończyć pracę. Serwer raz uruchomiony pracuje aż do zabicia procesu.
# W wariancie Python należy początkowo w kodzie klienta i serwera użyć funkcji `sendall()`.
# Serwer wyprowadza na stdout adres dołączonego klienta.

BUFSIZE = 10


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


def handle_received_stream(s: socket.socket) -> None:
    try:
        message = bytearray()
        data = b'1'
        while data:
            data = s.recv(BUFSIZE)
            print(data)
            message += data

        print(f'Message received: {message.decode("ascii")}')
    except socket.error as socketError:
        print(f'Error while receiving data: {socketError}')
    except UnicodeDecodeError as decodeError:
        print(f'Error while decoding received data: {decodeError}')


def prepare_socket_and_start_listening(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        bind_address(s, host, port)
        s.listen(10)

        while work():
            connectedSocket, address = s.accept()
            print(f'Client address: {address}')
            handle_received_stream(connectedSocket)


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
