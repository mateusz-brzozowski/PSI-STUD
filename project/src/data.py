from coordinates import Coordinates


class Data:
    data_stream_id: int

    # timestamp (e.g. 31.12.2022 15:05:46.5946002 → 1672495546.5946002)
    time: float

    content: bytes
    coordinates: Coordinates
