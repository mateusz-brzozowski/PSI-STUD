from packet import Packet
from typing import Optional


class SessionManager:
    session_id: int
    session_key: str
    public_key: str
    private_key: str
    sender_public_key: str
    # database: Database

    def handle(self, packet: Packet) -> Optional[Packet]:
        return packet
