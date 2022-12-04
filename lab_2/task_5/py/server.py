# Laboratorium 2 Zadanie 2.5 Serwer w Pythonie
# Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk,
#          Jakub Marcowski, Aleksandra Sypuła
# Data ukończenia: 04.12.2022

import os
import socket
import sys
import threading
from typing import List, Tuple

# Na bazie wersji 2.1 – 2.2 zmodyfikować serwer tak, aby miał
# konstrukcję współbieżną, tj. obsługiwał każdego klienta
# w osobnym procesie. Należy posłużyć się wątkami, do wyboru:
# wariant podstawowy lub skorzystanie z ThreadPoolExecutor.

BUF_SIZE = 10


def parse_arguments(args: List[str]) -> Tuple[str, int]:
    if len(args) < 3:
        print("No host and/or port defined,",
              "using localhost at 8000 as default")
        host = "127.0.0.1"
        port = 8000
    else:
        host = sys.argv[1]
        port = int(sys.argv[2])

    print(f"Will listen on {host}:{port}")

    return host, port


def bind_address(s: socket.socket, host: str, port: int) -> None:
    try:
        s.bind((host, port))
    except socket.error as exception:
        raise socket.error("Error while binding",
                           f"address to socket: {exception}") from exception


def multithreaded_stream(connection: socket.socket) -> None:
    while message := connection.recv(BUF_SIZE):
        print(f"Thread id: {threading.get_native_id()},",
              f"received message: {message.decode('utf-8')}")
    connection.close()


def prepare_socket_and_start_listening(host: str, port: int) -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        bind_address(s, host, port)
        s.listen(10)
        print(f"TCP server up and listening on port {port}")

        print(f"To stop the server type 'kill {os.getpid()}'",
              "in a different terminal")
        while True:
            connected_socket, address = s.accept()
            print(f"Connected to client from host {address[0]},",
                  f"on port {address[1]}")
            threading.Thread(target=multithreaded_stream,
                             args=(connected_socket, )).start()


def main(args: List[str]) -> None:

    try:
        (host, port) = parse_arguments(args)
    except ValueError as exception:
        print(f"Error while parsing arguments: {exception}")
        return

    try:
        prepare_socket_and_start_listening(host, port)
    except socket.error as exception:
        print(f"Caught exception: {exception}")


if __name__ == "__main__":
    main(sys.argv)
