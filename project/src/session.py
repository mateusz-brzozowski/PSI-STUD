import sys
from typing import List

from data import Data
from database import Database
from packet import Packet, packet_type_client, packet_type_server
from utility import bytes_to_datetime


class SessionManager:
    """
    Zarządca sesji:
    - przechowuje informacje o aktywnej sesji
    - zachowuje informacje o stanie danego połączenia np.
        - adres IP oraz port klienta
        - id sesji
        - fazie sesji (nawiązywanie połączenia, uzgadnianie klucza,
        przesyłanie danych)
        - ustalony klucz sesyjny
        - ilość strumieni danych
    - obsługuje otrzymywane pakiety
    - uzgadnia klucz sesyjny
    - deszyfruje pakiety
    - decyduje czy dany pakiet ma sens w kontekście danej sesji
    - przygotowuje komunikaty (odpowiedzi) do przesłania do klienta
        - przekazuje je odbiorcy do wysłania
        - potwierdza wszystkie otrzymane poprawne pakiety
    - rozdziela poszczególne strumienie danych do odpowiednich miejsc
    w bazie danych
    """

    state: int
    session_id: int
    session_key: str
    public_key: str
    private_key: str
    sender_public_key: str
    database: Database

    def __init__(self, host: str, port: int, database: Database) -> None:
        self.host = host
        self.port = port
        self.database = database
        self.state = session_manager_states["INIT"]

    def handle(self, packet: Packet) -> Packet:
        packet_type = packet.content()[:3]
        if packet_type == packet_type_client["initial"]:
            return self.handle_init()
        elif packet_type == packet_type_client["session_data"]:
            return self.handle_session_data(packet)
        elif packet_type == packet_type_client["declaration"]:
            return self.handle_declaration(packet)
        elif packet_type == packet_type_client["send"]:
            return self.handle_send(packet)
        elif packet_type == packet_type_client["close"]:
            return self.handle_close()
        else:
            return Packet(packet_type_server["error"])

    def handle_init(self) -> Packet:
        """
        Metoda pomocnicza służąca
        potwierdzeniu otwarcia sesji
        """
        if self.state != session_manager_states["INIT"]:
            self.state = session_manager_states["ERROR"]
            return Packet(packet_type_server["error"])
        self.state = session_manager_states["SYMMETRIC_KEY_NEGOTIATION"]
        return Packet(packet_type_server["initial"])

    def handle_session_data(self, packet: Packet) -> Packet:
        """
        Metoda pomocnicza służąca
        uzgodnieniu klucza symetrycznego
        """
        if self.state != session_manager_states["SYMMETRIC_KEY_NEGOTIATION"]:
            self.state = session_manager_states["ERROR"]
            return Packet(packet_type_server["error"])
        server_public_key_A = packet.content()[3:67]
        public_primitive_root_base_g = packet.content()[67:99]
        public_prime_modulus_p = packet.content()[99:131]
        server_public_key_B = bytes(12345)  # TODO: wygenerować klucz publiczny
        self.state = session_manager_states["SESSION_CONFIRMATION"]
        return Packet(packet_type_server["session_data"] + server_public_key_B)

    def handle_declaration(self, packet: Packet) -> Packet:
        """
        Metoda pomocznicza służąca
        potwierdzeniu odebrania informacji o sesji
        """
        if self.state != session_manager_states["SESSION_CONFIRMATION"]:
            self.state = session_manager_states["ERROR"]
            return Packet(packet_type_server["error"])
        stream_count = packet.content()[3:6]
        self.stream_ids = [
            packet.content()[i : i + 128]
            for i in range(6, 6 + int(stream_count) * 128, 128)
        ]
        self.state = session_manager_states["DATA_TRANSFER"]
        return Packet(packet_type_server["acknowledge"])

    def handle_send(self, packet: Packet) -> Packet:
        """
        Metoda pomocnicza służąca
        potwierdzeniu odbioru paczki danych
        """
        if self.state != session_manager_states["DATA_TRANSFER"]:
            self.state = session_manager_states["ERROR"]
            return Packet(packet_type_server["error"])
        datagram_num = packet.content()[3:19]
        data = packet.content()[19:]
        data_entry_len = 67  # 3 + 32 + 32
        data_entries = [
            data[i : i + data_entry_len]
            for i in range(0, len(data), data_entry_len)
        ]
        for data_entry in data_entries:
            stream_id = data_entry[:3]
            timestamp = data_entry[3:35]
            data = data_entry[35:]
            new_data_entry = Data(
                int(stream_id), bytes_to_datetime(timestamp), data
            )
            self.database.insert(new_data_entry, (self.host, self.port))
        self.state = session_manager_states["SESSION_CLOSING"]
        return Packet(packet_type_server["receive"] + datagram_num)

    def handle_close(self) -> Packet:
        """
        Metoda pomocnicza służąca
        potwierdzeniu zamknięcia sesji
        """
        if self.state != session_manager_states["SESSION_CLOSING"]:
            self.state = session_manager_states["ERROR"]
            return Packet(packet_type_server["error"])
        self.state = session_manager_states["INIT"]
        return Packet(packet_type_server["close"])


session_manager_states = {
    "INIT": 0,
    "SYMMETRIC_KEY_NEGOTIATION": 1,
    "SESSION_CONFIRMATION": 2,
    "DATA_TRANSFER": 3,
    "SESSION_CLOSING": 4,
    "ERROR": 5,
}


def main(args: List[str]) -> None:
    db = Database()
    session_manager = SessionManager("localhost", 8080, db)
    session_manager.handle(Packet(b"000"))  # type

    # needs need synthetic data

    # session_manager.handle(
    #     Packet(
    #         b"001"  # type
    #         + b"1010010101100010"
    #         + b"1010010101100010"
    #         + b"1010010101100010"
    #         + b"1010010101100010"  # server A's public key
    #     )
    # )
    # session_manager.handle(Packet(b"010"))  # type
    # session_manager.handle(
    #     Packet(b"011" + b"1010010101100010")  # type  # datagram num
    # )
    # session_manager.handle(Packet(b"100"))  # type
    # session_manager.handle(Packet(b"101"))  # type


if __name__ == "__main__":
    main(sys.argv)
