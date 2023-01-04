import sys
from datetime import datetime
from typing import List

from data import Data
from database import Database
from packet import Packet, packet_type_client, packet_type_server
from utility import unpack


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
        packet_type = packet.content()[:1]
        print(f"Packet type: {packet_type.decode()}")
        if packet_type == packet_type_client["initial"].encode():
            return self.handle_init()
        elif packet_type == packet_type_client["session_data"].encode():
            return self.handle_session_data(packet)
        elif packet_type == packet_type_client["declaration"].encode():
            return self.handle_declaration(packet)
        elif packet_type == packet_type_client["send"].encode():
            return self.handle_send(packet)
        elif packet_type == packet_type_client["close"].encode():
            return self.handle_close()
        else:
            return self.handle_error()

    def handle_init(self) -> Packet:
        """
        Metoda pomocnicza służąca
        potwierdzeniu otwarcia sesji
        """
        return self.simple_ack("INIT", "SYMMETRIC_KEY_NEGOTIATION", "initial")

    def handle_session_data(self, packet: Packet) -> Packet:
        """
        Metoda pomocnicza służąca
        uzgodnieniu klucza symetrycznego
        """
        if self.state != session_manager_states["SYMMETRIC_KEY_NEGOTIATION"]:
            self.state = session_manager_states["ERROR"]
            return self.handle_error()
        # server_public_key_A = packet.content()[3:67]
        # public_primitive_root_base_g = packet.content()[67:99]
        # public_prime_modulus_p = packet.content()[99:131]
        server_public_key_B = bytes(12345)  # TODO: wygenerować klucz publiczny
        self.state = session_manager_states["SESSION_CONFIRMATION"]
        return Packet(
            packet_type_server["session_data"].encode() + server_public_key_B
        )

    def handle_declaration(self, packet: Packet) -> Packet:
        """
        Metoda pomocznicza służąca
        potwierdzeniu odebrania informacji o sesji
        """
        if (
            self.state != session_manager_states["SYMMETRIC_KEY_NEGOTIATION"]
        ):  # TODO: change to SESSION_CONFIRMATION
            self.state = session_manager_states["ERROR"]
            return self.handle_error()
        stream_count = packet.content().decode()[1]
        self.stream_ids = [
            str(packet.content()[i : i + 16].decode()).strip()
            for i in range(2, 2 + int(stream_count) * 16, 16)
        ]
        self.state = session_manager_states["DATA_TRANSFER"]
        return Packet(packet_type_server["acknowledge"].encode())

    def handle_send(self, packet: Packet) -> Packet:
        """
        Metoda pomocnicza służąca
        potwierdzeniu odbioru paczki danych
        """
        if self.state != session_manager_states["DATA_TRANSFER"]:
            self.state = session_manager_states["ERROR"]
            return self.handle_error()
        datagram_num = packet.content()[1:3]
        data = packet.content()[3:]
        data_entry_len = 9  # 1 + 4 + 4
        data_entries = [
            data[i : i + data_entry_len]
            for i in range(0, len(data), data_entry_len)
        ]
        for data_entry in data_entries:
            stream_id = data_entry[0]
            timestamp = unpack(data_entry[1:5])
            data = data_entry[5:]
            new_data_entry = Data(
                self.stream_ids[stream_id],
                datetime.fromtimestamp(timestamp),
                data,
            )
            self.database.insert(new_data_entry, (self.host, self.port))
        # self.state = session_manager_states["SESSION_CLOSING"]
        return Packet(packet_type_server["receive"].encode() + datagram_num)

    def handle_close(self) -> Packet:
        """
        Metoda pomocnicza służąca
        potwierdzeniu zamknięcia sesji
        """
        return self.simple_ack("SESSION_CLOSING", "INIT", "close")

    def simple_ack(
        self, expected_state: str, next_state: str, return_packet_type: str
    ) -> Packet:
        if self.state != session_manager_states[expected_state]:
            self.state = session_manager_states["ERROR"]
            return self.handle_error()
        self.state = session_manager_states[next_state]
        return Packet(packet_type_server[return_packet_type].encode())

    def handle_error(self) -> Packet:
        """
        Metoda pomocnicza służąca
        wysyłaniu kodu błędu
        """
        self.state = session_manager_states["INIT"]
        return Packet(packet_type_server["terminal"].encode())


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
