# Laboratorium 1 Zadanie 1.2 Klient w Pythonie
# Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk, Jakub Marcowski, Aleksandra Sypuła
# Data ukończenia: 27.11.2022

import socket
import sys
from typing import List, Tuple
import random
import string

# Klient wysyła a serwer odbiera datagramy o przyrastającej wielkości. 
# Sprawdzić jaki był maksymalny rozmiar wysłanego (przyjętego) datagramu. 
# Ustalić z dokładnością do jednego bajta jak duży datagram jest obsługiwany.

DATA_GRAM_ADD = 1 # # how much to add to next datagrams
DATA_GRAM_MULT = 1.1 # how many times bigger are next datagrams
DATA_GRAM_START_LEN = 65506
MSG_TOO_LONG=False


def get_random_string(length: int) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def parse_arguments(args: List[str]) -> Tuple[str, int]:
    if len(args) < 3:
        print('No host or port defined, using localhost at 8000 as default')
        host = 'localhost'
        port = 8000
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    host_address = socket.gethostbyname(host)
    print(f'Will send to {host}:{port} at {host_address}:{port}')

    return host_address, port


def connect_with_server(s: socket.socket, host: str, port: int) -> None:
    try:
        s.connect((host, port))
    except socket.error as exception:
        raise socket.error(
            f'Error while connecting: {exception}'
        )


def send_text(s: socket.socket, text: str) -> None:
    print('Sending data')
    try:
        s.send(text.encode('ascii'))
    except socket.error as exception:
        print(f'Exception while sending data: {exception}')
        global MSG_TOO_LONG
        MSG_TOO_LONG=True
    except UnicodeEncodeError as exception:
        print(f'Exception while encoding text to bytes: {exception}')


def prepare_socket_and_start_sending_data(host: str, port: int) -> None:

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        connect_with_server(s, host, port)
        datagram_len = DATA_GRAM_START_LEN
        while work():
            send_text(s, get_random_string(int(datagram_len)))
            datagram_len += DATA_GRAM_ADD
            # datagram_len *= DATA_GRAM_MULT

def work() -> bool:
    if MSG_TOO_LONG:
        return False
    return True

def main(args: List[str]) -> None:
    try:
        (host, port) = parse_arguments(args)
    except socket.error as exception:
        print(f'Get host by name raised an exception: {exception}')
        return
    except ValueError as exception:
        print(f'Error while parsing arguments: {exception}')
        return

    try:
        prepare_socket_and_start_sending_data(host, port)
    except socket.error as exception:
        print(f'Caught exception: {exception}')

    print('Client finished.')


if __name__ == '__main__':
    main(sys.argv)
