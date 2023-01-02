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

        # data.content = bytes (as of now), not float
        new_entry = DataEntry(data.time, data.content)

        if key not in self.data.keys():
            self.data[key] = [new_entry]
        else:
            self.data[key].append(new_entry)


def address_id(stream_id: int, address: str, port: int) -> str:
    return f"{address}:{port}:{stream_id}"
