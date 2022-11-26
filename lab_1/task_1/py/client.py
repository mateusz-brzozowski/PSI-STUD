import socket
import sys
from typing import List, Tuple
import random
import string

# Klient wysyła a serwer odbiera datagramy o stałym, niewielkim rozmiarze (rzędu kilkudziesięciu bajtów).
# Datagramy mogą zawierać ustalony „na sztywno” lub generowany napis – np. „abcde….”, „bcdef…​”, itd.
# Powinno być wysyłanych kilka datagramów, po czym klient powinien kończyć pracę.
# Serwer raz uruchomiony pracuje aż do zabicia procesu. Serwer wyprowadza na stdout adres klienta przysyłającego datagram.

DATA_GRAM_LENGTH = 60
DATA_GRAM_NUMBER = 10


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
    print(f'Sending {text}')
    try:
        s.send(text.encode('ascii'))
    except socket.error as exception:
        print(f'Exception while sending data: {exception}')
    except UnicodeEncodeError as exception:
        print(f'Exception while encoding text to bytes: {exception}')


def prepare_socket_and_start_sending_data(host: str, port: int) -> None:
    data_grams: List[str] = [
        get_random_string(DATA_GRAM_LENGTH)
        for _ in range(DATA_GRAM_NUMBER)
    ]

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        connect_with_server(s, host, port)

        for text in data_grams:
            send_text(s, text)


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
