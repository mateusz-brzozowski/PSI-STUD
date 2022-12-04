# Laboratorium 2 Zadanie 2.5 Serwer w Pythonie
# Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk,
#          Jakub Marcowski, Aleksandra Sypuła
# Data ukończenia: 04.12.2022

import socket
import sys
from typing import List, Tuple
import random
import string

# Na bazie wersji 2.1 – 2.2 zmodyfikować serwer tak, aby miał
# konstrukcję współbieżną, tj. obsługiwał każdego klienta
# w osobnym procesie. Należy posłużyć się wątkami, do wyboru:
# wariant podstawowy lub skorzystanie z ThreadPoolExecutor.

DATAGRAM_LENGTH = 60
DATAGRAM_NUMBER = 10


def get_random_string(length: int) -> str:
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def parse_arguments(args: List[str]) -> Tuple[str, int]:
    if len(args) < 3:
        print("No host and/or port defined,",
              "using localhost at 8000 as default")
        host = "localhost"
        port = 8000
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    host_address = socket.gethostbyname(host)
    print(f"Will send to {host}:{port} at {host_address}:{port}")

    return host_address, port


def connect_with_server(s: socket.socket, host: str, port: int) -> None:
    try:
        s.connect((host, port))
    except socket.error as exception:
        raise socket.error("Error while connecting:",
                           exception) from exception


def send_text(s: socket.socket, text: str) -> None:
    print(f"Sending {text}")
    try:
        s.sendall(text.encode("ascii"))
    except socket.error as exception:
        print(f"Exception while sending data: {exception}")
    except UnicodeEncodeError as exception:
        print(f"Exception while encoding text to bytes: {exception}")


def prepare_socket_and_start_sending_data(host: str, port: int) -> None:
    datagrams: List[str] = [
        get_random_string(DATAGRAM_LENGTH)
        for _ in range(DATAGRAM_NUMBER)
    ]

    for text in datagrams:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            connect_with_server(s, host, port)
            send_text(s, text)


def main(args: List[str]) -> None:
    try:
        (host, port) = parse_arguments(args)
    except socket.error as exception:
        print(f"Get host by name raised an exception: {exception}")
        return
    except ValueError as exception:
        print(f"Error while parsing arguments: {exception}")
        return

    try:
        prepare_socket_and_start_sending_data(host, port)
    except socket.error as exception:
        print(f"Caught exception: {exception}")

    print("Client finished.")


if __name__ == "__main__":
    main(sys.argv)
