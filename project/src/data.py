# Projekt
# Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk, Jakub Marcowski, Aleksandra Sypuła
# Data ukończenia: 16.01.2023

from datetime import datetime


class Data:
    data_stream_id: str
    time: datetime
    content: bytes

    def __init__(
        self, data_stream_id: str, time: datetime, content: bytes
    ) -> None:
        self.data_stream_id = data_stream_id
        self.time = time
        self.content = content
