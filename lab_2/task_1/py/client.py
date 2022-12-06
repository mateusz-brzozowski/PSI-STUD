# Laboratorium 1 Zadanie 1.1 Klient w Pythonie
# Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk, Jakub Marcowski, Aleksandra Sypuła
# Data ukończenia: 27.11.2022

import socket
import sys
from typing import List, Tuple
import random
import string

# Klient wysyła a serwer odbiera porcje danych o stałym, niewielkim rozmiarze (rzędu kilkudziesięciu bajtów).
# Mogą one zawierać ustalony „na sztywno” lub generowany napis – np. „abcde….”, „bcdef…​”, itd.
# Po wysłaniu danych klient powinien kończyć pracę. Serwer raz uruchomiony pracuje aż do zabicia procesu.
# W wariancie Python należy początkowo w kodzie klienta i serwera użyć funkcji `sendall()`.
# Serwer wyprowadza na stdout adres dołączonego klienta.

DATA_GRAM_LENGTH = 60
DATA_GRAM_NUMBER = 10


def get_random_string(length: int) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def parse_arguments(args: List[str]) -> Tuple[str, int, bool]:
    if len(args) < 4:
        print('No host and/or port defined, using localhost at 8000 as default')
        host = 'localhost'
        port = 8000
        send_all = True
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])
        send_all = sys.argv[3].lower() == 'true'

    host_address = socket.gethostbyname(host)
    print(f'Will send to {host}:{port} at {host_address}:{port}')

    return host_address, port, send_all


def connect_with_server(s: socket.socket, host: str, port: int) -> None:
    try:
        s.connect((host, port))
    except socket.error as exception:
        raise socket.error(
            f'Error while connecting: {exception}'
        )


def send_all_using_send(s: socket.socket, data: bytes) -> None:
    returned: int = s.send(data)
    print(f'Data sent: {data[:returned]}')
    print(f'Data length sent: {returned}')
    data = data[returned:]

    while returned > 0 and len(data) > 0:
        returned: int = s.send(data)
        print(f'Data sent: {data[:returned]}')
        print(f'Data length sent: {returned}')
        data = data[returned:]


def send_text(s: socket.socket, text: str, send_all: bool) -> None:
    print(f'Sending {text}')
    try:
        if send_all:
            s.sendall(text.encode('ascii'))
        else:
            send_all_using_send(s, text.encode('ascii'))
    except socket.error as exception:
        print(f'Exception while sending data: {exception}')
    except UnicodeEncodeError as exception:
        print(f'Exception while encoding text to bytes: {exception}')


def prepare_socket_and_start_sending_data(host: str, port: int, send_all: bool) -> None:
    data_grams: List[str] = [
        get_random_string(DATA_GRAM_LENGTH)
        for _ in range(DATA_GRAM_NUMBER)
    ]

    for text in data_grams:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            connect_with_server(s, host, port)
            send_text(s, text, send_all)


def main(args: List[str]) -> None:
    try:
        (host, port, send_all) = parse_arguments(args)
    except socket.error as exception:
        print(f'Get host by name raised an exception: {exception}')
        return
    except ValueError as exception:
        print(f'Error while parsing arguments: {exception}')
        return

    try:
        prepare_socket_and_start_sending_data(host, port, send_all)
    except socket.error as exception:
        print(f'Caught exception: {exception}')

    print('Client finished.')


if __name__ == '__main__':
    main(sys.argv)
