from typing import Optional

from packet import Packet


class SessionManager:
    session_id: int
    session_key: str
    public_key: str
    private_key: str
    sender_public_key: str
    # database: Database

    def __init__(self, host: str, port: int) -> None:
        pass

    def handle(self, packet: Packet) -> Optional[Packet]:
        return packet
