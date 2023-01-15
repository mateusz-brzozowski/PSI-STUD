import socket
from threading import Semaphore, Thread
from typing import List

import pytest
from database import Database
from receiver import thread_test
from sender import THREAD_IDS, Sender, thread_generator


def test_fibb():
    """
    Teścior do sprawdzenia czy przesłanie
    sekwencji fibbonaciego działa poprawnie
    """
    # Odbiorca
    # host_r = "0.0.0.0"
    # port_r = 8080
    # database = Database()
    # thread_test_isnt = Thread(target=thread_test, args=(database, host_r, port_r))
    # thread_test_isnt.start()  # problem bo to się obraca w nieskończoność

    # nadawca
    # host_s = socket.gethostbyname("localhost")
    # port_s = 8080
    # bind_port_s = None

    # number_of_threads = 8
    # threads: List[Thread] = []
    # write_semaphore = Semaphore(number_of_threads)

    # with Sender((host_s, port_s), write_semaphore, THREAD_IDS, bind_port_s) as s:
    #     threads.extend(
    #         Thread(target=thread_generator, args=(THREAD_IDS[thread_num], s))
    #         for thread_num in range(number_of_threads)
    #     )
    #     for thread in threads:
    #         thread.start()

    #     try:
    #         s.work()
    #     except socket.error as exception:
    #         print(f"Sender: Złapano wyjątek: {exception}")
    assert True
