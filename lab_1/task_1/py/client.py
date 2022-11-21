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

    print(f'Will send to {host}:{port}')
    host = socket.gethostbyname(host)
    print(f'at {host}:{port}')

    return host, port


def send_text(s: socket.socket, text: str) -> None:
    s.send(text.encode('ascii'))


def main(args: List[str]) -> None:

    data_grams: List[str] = [
        get_random_string(DATA_GRAM_LENGTH)
        for _ in range(DATA_GRAM_NUMBER)
    ]

    (host, port) = parse_arguments(args)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect((host, port))
        for text in data_grams:
            # send_text(s, text)
            s.sendto(text.encode('ascii'), (host, port))

    print('Client finished.')


if __name__ == '__main__':
    main(sys.argv)
