from datetime import datetime
from typing import Dict, Tuple

from data import Data


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

    data: Dict  # Mapping

    def __init__(self) -> None:
        self.data = {}

    def insert(self, data: Data, address: Tuple[str, int]) -> None:
        key = address_id(data.data_stream_id, address[0], address[1])

        content_as_float = float(data.content.decode())
        new_entry = DataEntry(data.time, content_as_float)

        if key not in self.data.keys():
            self.data[key] = [new_entry]
        else:
            self.data[key].append(new_entry)

        print(f"New data from {data.time} received from {key}.")
        print(f"Data: {data.content}")

    def clients_address(self) -> list:
        clients_addr = set([':'.join(x.split(':')[:-1]) for x in self.data.keys()])
        return list(clients_addr)


def address_id(stream_id: str, address: str, port: int) -> str:
    return f"{address}:{port}:{stream_id}"
