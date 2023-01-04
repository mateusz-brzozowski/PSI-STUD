from datetime import datetime, timedelta
from multiprocessing import Process
from multiprocessing.managers import BaseManager
from time import sleep
from typing import List

import matplotlib.pyplot as plt  # type: ignore
import numpy as np
import seaborn as sns  # type: ignore
from data import Data
from database import Database
from matplotlib.animation import FuncAnimation  # type: ignore

sns.set_style("darkgrid")

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
    clients: List[str]
    streams: int

    def __init__(self, database: Database, streams: int = 8):
        print(database)
        print(database.get_data())
        self.database = database
        self.streams = streams
        self.init_dashboard()
        self.show()

    def animate(self, i: int) -> None:
        i = 0
        for client in self.database.clients_address():

            self.axis[i].set_title(f"Data source: {client}")

            for stream in self.database.client_streams(client):
                xdata: List[datetime] = []
                ydata: List[float] = []

                data = self.database.get_data()[f"{client}:{stream}"]

                for entry in data[-SIZE:]:
                    xdata.append(entry.time)
                    ydata.append(entry.value)
                    self.axis[i].clear()
                    self.axis[i].plot(
                        xdata, ydata, "o", label=f"Stream {stream}"
                    )
            i = i + 1
            if i > MAX_CLIENTS:
                break

        sleep(1)
        print(self.database.get_data())

    def init_dashboard(self) -> None:
        self.fig, self.axis = plt.subplots(MAX_CLIENTS)

    def show(self) -> None:
        anim = FuncAnimation(
            self.fig, self.animate, frames=np.array(list(range(40)))
        )
        plt.show()


# def get_vals_from_key(key: str) -> List[str]:
#     stream_id, address, port = key.split(":")
#     return [stream_id, address, port]


# def title_with_address(key: str) -> str:
#     address, port = get_vals_from_key(key)[1:]
#     return f"Data source: {address}:{port}"


def main():
    BaseManager.register(typeid="Database", callable=Database, exposed=("get_data", "insert", "clients_address", "client_streams"))
    manager = BaseManager()
    manager.start()
    database: Database = manager.Database()
    data = Data("s", datetime.now(), b"7")
    database.insert(data, ("localhost", 8080))
    data_2 = Data("s", datetime.now() + timedelta(days=180), b"10")
    database.insert(data_2, ("localhost", 8080))
    interface_proc = Process(target=Interface, args=(database,))
    interface_proc.start()
    sleep(5)
    data_3 = Data("s", datetime.now() + timedelta(days=360), b"12")
    database.insert(data_3, ("localhost", 8080))


if __name__ == "__main__":
    main()
