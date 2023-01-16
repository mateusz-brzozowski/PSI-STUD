import multiprocessing as mp
import socket
from datetime import datetime
from threading import Semaphore, Thread
from typing import List

from data import Data
from database import Database
from receiver import Receiver
from sender import THREAD_IDS, Sender
from utility import pack

# --- sender's functions for testing ---


def fib(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, (a + b)
    return a


def fib_generator(id: str, sender: Sender) -> None:
    counter = 0
    while True:
        num = fib(counter)
        if num > 2971215073:  # we don't need to go further than this number
            break
        sender.save_data_to_buffer(Data(id, datetime.now(), pack(num, 4)))
        counter += 1


def sender_proc() -> None:
    host_s = socket.gethostbyname("localhost")
    port_s = 8080
    bind_port_s = None

    write_semaphore = Semaphore(1)

    sender = Sender((host_s, port_s), write_semaphore, THREAD_IDS, bind_port_s)
    thread_fib = Thread(target=fib_generator, args=(THREAD_IDS[1], sender))
    thread_fib.start()
    sender.work()


# --- receiver's functions for testing ---


def listen_test(
    receiver: Receiver, host: str = "0.0.0.0", port: int = 8080
) -> None:
    receiver.bind_address(host, port)

    while receiver._work:
        address, datagram = receiver.receive_datagram()

        if address and datagram:
            if datagram := receiver.handle(address, datagram):
                receiver.send_datagram(address, datagram)

        if receiver._database.data:
            receiver._work = False


def thread_test(database: Database, host: str, port: int) -> None:
    receiver = Receiver(database)
    listen_test(receiver, host, port)


# --- tests ---


def test_fib() -> None:
    """
    Test sprawdzający, czy przesłanie
    sekwencji fibonacciego działa poprawnie
    """

    # Odbiorca
    host_r = "0.0.0.0"
    port_r = 8080
    database = Database()
    thread_receiver = Thread(
        target=thread_test, args=(database, host_r, port_r)
    )
    thread_receiver.start()

    # nadawca
    proc = mp.Process(target=sender_proc, args=())
    proc.start()
    thread_receiver.join()
    proc.terminate()  # sends a SIGTERM
    proc.join()  # waits for the process to terminate

    # sprawdzenie
    expected = [
        0,
        1,
        1,
        2,
        3,
        5,
        8,
        13,
        21,
        34,
        55,
        89,
        144,
        233,
        377,
        610,
        987,
        1597,
        2584,
        4181,
        6765,
        10946,
        17711,
        28657,
        46368,
        75025,
        121393,
        196418,
        317811,
        514229,
        832040,
        1346269,
        2178309,
        3524578,
        5702887,
        9227465,
        14930352,
        24157817,
        39088169,
        63245986,
        102334155,
        165580141,
        267914296,
        433494437,
        701408733,
        1134903170,
        1836311903,
        2971215073,
    ]

    actual: List[int] = []
    for data in database.data.values():
        actual.extend(int(data_entry.value) for data_entry in data)

    assert actual == expected


if __name__ == "__main__":
    test_fib()
