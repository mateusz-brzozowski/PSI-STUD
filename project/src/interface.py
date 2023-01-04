from datetime import datetime
from multiprocessing import Process
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

                data = self.database.data[f"{client}:{stream}"]

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

    def init_dashboard(self) -> None:
        self.fig, self.axis = plt.subplots(MAX_CLIENTS)

    def show(self) -> None:
        ani = FuncAnimation(
            self.fig, self.animate, frames=np.array(list(range(40)))
        )
        ani.resume()  # so that the linter shuts up
        plt.show()


# def get_vals_from_key(key: str) -> List[str]:
#     stream_id, address, port = key.split(":")
#     return [stream_id, address, port]


# def title_with_address(key: str) -> str:
#     address, port = get_vals_from_key(key)[1:]
#     return f"Data source: {address}:{port}"


def main():
    database = Database()
    print(database)
    interface_proc = Process(target=Interface, args=(database,))
    interface_proc.start()
    sleep(5)
    print("uga buga")
    data = Data("sen_1", datetime.now(), b"107.0")
    database.insert(data, ("localhost", 8080))
    print(database)


if __name__ == "__main__":
    main()
