# Laboratorium 1 Zadanie 1.2 Klient w Pythonie
# Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk, Jakub Marcowski, Aleksandra Sypuła
# Data ukończenia: 28.11.2022

import socket
import sys
from typing import List, Tuple
import random
import string

# Klient wysyła a serwer odbiera datagramy o przyrastającej wielkości.
# Sprawdzić jaki był maksymalny rozmiar wysłanego (przyjętego) datagramu.
# Ustalić z dokładnością do jednego bajta jak duży datagram jest obsługiwany.


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


def send_text(s: socket.socket, length: int) -> bool:
    print(f'Trying to send data with length: {length}')
    try:
        s.send(get_random_string(length).encode('ascii'))
    except socket.error as exception:
        print(f'Exception while sending data: {exception}')
        return False
    except UnicodeEncodeError as exception:
        print(f'Exception while encoding text to bytes: {exception}')
        return False
    return True


def prepare_socket_and_start_sending_data(host: str, port: int) -> int:

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        connect_with_server(s, host, port)
        data_length: int = 1
        jump: int = 2
        JUMP_MULTIPLIER: float = 2.0
        while work(jump):
            if send_text(s, data_length + jump):
                data_length += jump
                jump = int(jump * JUMP_MULTIPLIER)
            else:
                jump = int(jump / JUMP_MULTIPLIER)
        return data_length


def work(jump_size: int) -> bool:
    if jump_size == 0:
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
        max_data_length = prepare_socket_and_start_sending_data(host, port)
        print(f'Max data length: {max_data_length}')
    except socket.error as exception:
        print(f'Caught exception: {exception}')

    print('Client finished.')


if __name__ == '__main__':
    main(sys.argv)
