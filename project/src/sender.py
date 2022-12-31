from queue import Queue
from typing import Tuple

from data import Data


class Sender:
    buffer: Queue[Data]
    session_key: str
    public_key: str
    private_key: str
    receiver_public_key: str

    def __init__(self, address: Tuple[str, int]) -> None:
        pass

    def send(self, content: bytes, stream_id: int) -> None:
        pass
