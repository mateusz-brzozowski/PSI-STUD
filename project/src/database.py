# Projekt - System niezawodnego strumieniowania danych po UDP
# Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk, Jakub Marcowski, Aleksandra Sypuła
# Data ukończenia: 16.01.2023

from datetime import datetime
from typing import Dict, List, Tuple

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

    clients: List[str]
    client_stream: Dict[str, List[str]]
    data: Dict[str, List[DataEntry]]

    def __init__(self) -> None:
        self.data = {}
        self.clients = []
        self.client_stream = {}

    def insert(self, data: Data, address: Tuple[str, int]) -> None:
        client = client_id(address[0], address[1])
        if client not in self.clients:
            self.clients.append(client)
        if client not in self.client_stream.keys():
            self.client_stream[client] = [data.data_stream_id]
        elif data.data_stream_id not in self.client_stream[client]:
            self.client_stream[client].append(data.data_stream_id)
        key = address_id(data.data_stream_id, address[0], address[1])

        value = unpack(data.content)
        new_entry = DataEntry(data.time, value)

        if key not in self.data.keys():
            self.data[key] = [new_entry]
        else:
            self.data[key].append(new_entry)

        print(
            f"Database: Nowe dane datowane na {data.time}"
            f"pochodzące od {key}: "
            f"{value}"
        )

    def clients_address(self) -> List[str]:
        return self.clients

    def client_streams(self, client_id: str) -> List[str]:
        return self.client_stream[client_id]


def client_id(address: str, port: int) -> str:
    return f"{address}:{port}"


def address_id(stream_id: str, address: str, port: int) -> str:
    return f"{address}:{port}:{stream_id}"
