import socket
import sys
from typing import List, Tuple

# Klient wysyła a serwer odbiera datagramy o stałym, niewielkim rozmiarze (rzędu kilkudziesięciu bajtów).
# Datagramy mogą zawierać ustalony „na sztywno” lub generowany napis – np. „abcde….”, „bcdef…​”, itd.
# Powinno być wysyłanych kilka datagramów, po czym klient powinien kończyć pracę.
# Serwer raz uruchomiony pracuje aż do zabicia procesu. Serwer wyprowadza na stdout adres klienta przysyłającego datagram.

BUFSIZE = 1024


def parse_arguments(args: List[str]) -> Tuple[str, int]:
    if len(args) < 3:
        print('No host or port defined, using localhost at 8000 as default')
        host = '127.0.0.1'  # Standard loopback interface address (localhost)
        port = 8000
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    print(f'Will send to {host}:{port}')

    return host, port


def work() -> bool:
    return True


def main(args: List[str]) -> None:

    (host, port) = parse_arguments(args)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((host, port))

        while work():
            (data, address) = s.recvfrom(BUFSIZE)

            print(f'Message received:{data}')
            print(f'Client IP Address:{address}')


if __name__ == '__main__':
    main(sys.argv)
