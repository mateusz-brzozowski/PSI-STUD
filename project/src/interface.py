import random
from datetime import datetime
from threading import Thread
from time import sleep
from typing import List

import matplotlib.pyplot as plt  # type: ignore
import numpy as np
import seaborn as sns  # type: ignore
from data import Data
from database import Database
from matplotlib.animation import FuncAnimation  # type: ignore
from utility import pack

sns.set_style("darkgrid")

COLORS = sns.color_palette("magma", 8)
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

    def animate(self, i: int) -> None:
        i = 0
        for client in self.database.clients_address():

            # self.axis[i].set_title(f"Data source: {client}")
            # print(self.database.client_streams(client))

            for stream in self.database.client_streams(client):
                xdata: List[datetime] = []
                ydata: List[float] = []

                data = self.database.data.get(f"{client}:{stream}")
                if data is None:
                    continue
                # print(f"{client}:{stream}")

                if self.database.client_streams(client).index(stream) == 0:
                    self.axis[i].clear()
                self.axis[i].set_title(f"Data source: {client}")
                # self.axis[i].set_xlim((datetime.now() - timedelta(seconds=5)).timestamp(), (datetime.now() + timedelta(seconds=5)).timestamp())
                self.axis[i].set_ylim(50, 1050)
                for entry in data[-SIZE:]:
                    # for entry in data:
                    xdata.append(entry.time)
                    ydata.append(entry.value)
                    # self.axis[i].clear()
                
                self.axis[i].plot(
                    xdata,
                    ydata,
                    "o-",
                    label=f"Stream {stream}",
                    color=COLORS[
                        self.database.client_streams(client).index(stream)
                    ],
                )
            self.axis[i].legend()
            i = i + 1
            if i > MAX_CLIENTS:
                break

        # sleep(1)

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


def insert_data(database: Database) -> None:
    while True:
        sleep(5)
        data = Data(
            "uga_buga",
            datetime.now(),
            pack(int(random.random() * 900 + 100), 4),
        )
        database.insert(data, ("localhost", 8080))


def main():
    database = Database()
    interface = Interface(database)
    ins_data = Thread(target=insert_data, args=(database,))
    ins_data.start()
    interface.show()


if __name__ == "__main__":
    main()
