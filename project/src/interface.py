from datetime import datetime
from time import sleep

import matplotlib.pyplot as plt  # type: ignore
import numpy as np
from typing import List

# from data import Data
from database import Database
from matplotlib.animation import FuncAnimation  # type: ignore

SIZE = 10
MAX_CLIENTS = 2

class Interface:
    """
    Interfejs aplikacji:
    - może działać na oddzielnym wątku od pozostałych komponentów
    - aplikacja monitorująca
    - wyświetla aktualny stan bazy danych w postaci wykresów
    """

    database: Database
    clients: list[str]
    streams: int

    def __init__(self, database: Database, streams: int = 8):
        self.database = database
        self.streams = streams
        self.init_dashboard()

    def animate(self, i: int):
        i = 0
        for client in self.database.clients_address():
            
            self.axis[i].set_title(f"Data source: {client}")
            
            for stream in self.database.client_streams(client):
                xdata: List[datetime] = []
                ydata: List[float] = []
                
                data = self.database.data[f"{client}:{stream}"]
                
                for entry in data[-SIZE:]:
                    xdata.append(entry.time)
                    ydata.append(entry.value)
                    self.axis[i].clear()
                    self.axis[i].plot(xdata, ydata, 'o', label=f"Stream {stream}")
            i = i + 1
            if i > MAX_CLIENTS:
                break

        sleep(1)
        # return

    def init_dashboard(self):
        self.fig, self.axis = plt.subplots(MAX_CLIENTS)

    def show(self) -> None:
        ani = FuncAnimation(
            self.fig, self.animate, frames=np.array(list(range(40)))
        )  # , init_func=self.beginning), blit=True)
        plt.show()


# def get_vals_from_key(key: str) -> list:
#     stream_id, address, port = key.split(":")
#     return [stream_id, address, port]


# def title_with_address(key: str) -> str:
#     address, port = get_vals_from_key(key)[1:]
#     return f"Data source: {address}:{port}"


def main():
    # db = Database()
    # data1 = Data()
    # db.insert()
    # interface = Interface("db_placeholder", 4)
    # interface.show()
    pass


if __name__ == "__main__":
    main()
