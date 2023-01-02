from datetime import datetime, timedelta
from time import sleep

import matplotlib.pyplot as plt  # type: ignore
import numpy as np

# from data import Data
from database import Database
from matplotlib.animation import FuncAnimation  # type: ignore

SIZE = 10

class Interface:
    """
    Interfejs aplikacji:
    - może działać na oddzielnym wątku od pozostałych komponentów
    - aplikacja monitorująca
    - wyświetla aktualny stan bazy danych w postaci wykresów
    """

    database: Database
    clients: list

    def __init__(self, database, streams=8):
        self.database = database
        self.streams = streams
        self.init_dashboard()

    def animate(self, i):
        i = 0
        for client in self.clients:
            for stream in self.streams:
                xdata, ydata = [], []
                #TODO: what if missing stream?
                data = self.database[f"{client}:{stream}"]
                for entry in data[-SIZE:]:
                    xdata.append(entry.time)
                    ydata.append(entry.data)
                    self.axis[i].clear()
                    self.axis[i].plot(xdata, ydata, 'o', label=f"Stream {stream}")
            i = i+1

        sleep(1)
        # return

    def init_dashboard(self):
        self.clients = self.database.clients_address()
        self.fig, self.axis = plt.subplots(self.clients)
        for i in range(self.clients):
            self.axis[i].set_title(f"Data source: {i}")

    def show(self):
        ani = FuncAnimation(
            self.fig, self.animate, frames=np.array(list(range(40)))
        )  # , init_func=self.beginning), blit=True)
        plt.show()


def get_vals_from_key(key: str) -> list:
    stream_id, address, port = key.split(":")
    return [stream_id, address, port]


def title_with_address(key: str) -> str:
    address, port = get_vals_from_key(key)[1:]
    return f"Data source: {address}:{port}"


def main():
    # db = Database()
    # data1 = Data()
    # db.insert()
    interface = Interface("db_placeholder", 4)
    interface.show()


if __name__ == "__main__":
    main()
