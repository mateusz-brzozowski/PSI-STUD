from datetime import datetime
from typing import Dict, List, Set, Tuple

from data import Data
from utility import unpack


class DataEntry:
    time: datetime
    value: float

    def __init__(self, time: datetime, value: float) -> None:
        self.time = time
        self.value = value


class Database:
    """
    Baza danych:
    - przechowuje uszeregowane dane według poszczególnych strumieni danych
    - agreguje wszystkie otrzymywane dane
    """

    clients: Set[str]
    client_stream: Dict[str, Set[str]]  # Mapping is too generic imo
    data: Dict[str, List[DataEntry]]

    def __init__(self) -> None:
        self.data = {}
        self.clients = set()
        self.client_stream = {}

    def insert(self, data: Data, address: Tuple[str, int]) -> None:
        client = client_id(address[0], address[1])
        self.clients.add(client)
        self.client_stream[client].add(data.data_stream_id)
        key = address_id(data.data_stream_id, address[0], address[1])

        # data.content = bytes (as of now), not float
        new_entry = DataEntry(data.time, unpack(data.content))

        if key not in self.data.keys():
            self.data[key] = [new_entry]
        else:
            self.data[key].append(new_entry)

        print(f"New data from {data.time} received from {key}.")
        print(f"Data: {data.content!r}")

    def clients_address(self) -> Set[str]:
        return self.clients

    def client_streams(self, client_id: str) -> Set[str]:
        return self.client_stream[client_id]


def client_id(address: str, port: int) -> str:
    return f"{address}:{port}"


def address_id(stream_id: str, address: str, port: int) -> str:
    return f"{address}:{port}:{stream_id}"
