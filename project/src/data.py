from datetime import datetime

from coordinates import Coordinates


class Data:
    data_stream_id: int
    time: datetime
    content: bytes
    coordinates: Coordinates
