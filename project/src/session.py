# Projekt - System niezawodnego strumieniowania danych po UDP
# Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk, Jakub Marcowski, Aleksandra Sypuła
# Data ukończenia: 16.01.2023

import sys
from datetime import datetime
from typing import List, Optional

import diffie_hellman
from data import Data
from database import Database
from packet import Packet, packet_type_client, packet_type_server
from utility import pack, unpack


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
    session_key: Optional[int]
    received_datagram_nr: Optional[int]
    public_key: int
    private_key: int
    sender_prime_number: int
    sender_primitive_root: int
    sender_public_key: int
    database: Database

    def __init__(self, host: str, port: int, database: Database) -> None:
        self.host = host
        self.port = port
        self.database = database
        self.state = session_manager_states["INIT"]
        self.private_key = diffie_hellman.generate_private_key()
        self.session_key = None
        self.received_datagram_nr = None

    def handle(self, packet: Packet) -> Optional[Packet]:
        if self.session_key:
            packet.decrypt(self.session_key)

        if len(packet.content()) < 1:
            return None

        packet_type = packet.msg_type()

        print(f"SessionManager: Typ pakietu: {packet_type}")

        if packet_type == packet_type_client["initial"]:
            datagram = self.handle_init()
        elif packet_type == packet_type_client["session_data"]:
            datagram = self.handle_session_data(packet)
        elif packet_type == packet_type_client["declaration"]:
            datagram = self.handle_declaration(packet)
            self.handle_encrypt(datagram)
        elif packet_type == packet_type_client["send"]:
            datagram = self.handle_send(packet)
            self.handle_encrypt(datagram)
        elif packet_type == packet_type_client["close"]:
            datagram = self.handle_close()
            self.handle_encrypt(datagram)
        else:
            datagram = self.handle_error()
            self.handle_encrypt(datagram)

        return datagram

    def handle_encrypt(self, datagram: Packet) -> None:
        if self.session_key:
            datagram.encrypt(self.session_key)

    def handle_init(self) -> Packet:
        """
        Metoda pomocnicza służąca
        potwierdzeniu otwarcia sesji
        """
        if self.state not in [
            session_manager_states["INIT"],
            session_manager_states["SYMMETRIC_KEY_NEGOTIATION"],
        ]:
            return self.handle_error()

        self.received_datagram_nr = None
        self.session_key = None
        self.state = session_manager_states["SYMMETRIC_KEY_NEGOTIATION"]
        return Packet(packet_type_server["initial"].encode())

    def handle_session_data(self, packet: Packet) -> Packet:
        """
        Metoda pomocnicza służąca
        uzgodnieniu klucza symetrycznego
        """

        if (
            self.state
            not in [
                session_manager_states["SYMMETRIC_KEY_NEGOTIATION"],
                session_manager_states["SESSION_CONFIRMATION"],
            ]
            or len(packet.content()) < 21
        ):
            return self.handle_error()

        self.sender_public_key = unpack(packet.content()[1:9])
        self.sender_primitive_root = unpack(packet.content()[9:13])
        self.sender_prime_number = unpack(packet.content()[13:21])

        self.public_key = diffie_hellman.calculate_public_key(
            self.sender_primitive_root,
            self.private_key,
            self.sender_prime_number,
        )
        self.session_key = diffie_hellman.get_session_key(
            self.sender_public_key, self.private_key, self.sender_prime_number
        )

        self.state = session_manager_states["SESSION_CONFIRMATION"]

        return Packet(
            packet_type_server["session_data"].encode()
            + pack(self.public_key, 8)
        )

    def handle_declaration(self, packet: Packet) -> Packet:
        """
        Metoda pomocznicza służąca
        potwierdzeniu odebrania informacji o sesji
        """
        if (
            self.state
            not in [
                session_manager_states["SESSION_CONFIRMATION"],
                session_manager_states["DATA_TRANSFER"],
            ]
            or len(packet.content()) < 18
        ):
            return self.handle_error()

        stream_count = unpack(packet.content()[1:2])

        if len(packet.content()) < 2 + stream_count * 16:
            return self.handle_error()

        self.stream_ids = [
            str(packet.content()[i: i + 16].decode()).strip()
            for i in range(2, 2 + stream_count * 16, 16)
        ]
        self.state = session_manager_states["DATA_TRANSFER"]
        return Packet(packet_type_server["acknowledge"].encode())

    def handle_send(self, packet: Packet) -> Packet:
        """
        Metoda pomocnicza służąca
        potwierdzeniu odbioru paczki danych
        """
        if (
            self.state != session_manager_states["DATA_TRANSFER"]
            or len(packet.content()) < 3
        ):
            return self.handle_error()

        datagram_num = unpack(packet.content()[1:3])
        data = packet.content()[3:]
        data_entry_len = 9  # 1 + 4 + 4
        data_entries = [
            data[i: i + data_entry_len]
            for i in range(0, len(data), data_entry_len)
        ]

        if self.received_datagram_nr != datagram_num:
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
            self.received_datagram_nr = datagram_num
        else:
            print("SessionManager: Już otrzymano pakiet o tym numerze")
        return Packet(
            packet_type_server["receive"].encode() + packet.content()[1:3]
        )

    def handle_close(self) -> Packet:
        """
        Metoda pomocnicza służąca
        potwierdzeniu zamknięcia sesji
        """
        if session_manager_states["SESSION_CLOSING"] != self.state:
            self.state = session_manager_states["ERROR"]
            return self.handle_error()
        self.state = session_manager_states["INIT"]
        return Packet(packet_type_server["close"].encode())

    def handle_error(self) -> Packet:
        """
        Metoda pomocnicza służąca
        wysyłaniu kodu błędu
        """
        self.session_key = None
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
    pass


if __name__ == "__main__":
    main(sys.argv)
