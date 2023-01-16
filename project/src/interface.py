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
from utility import pack, suppress_warings

sns.set_style("darkgrid")

COLORS = [
    (0.092949, 0.059904, 0.239164),
    (0.265447, 0.060237, 0.46184),
    (0.445163, 0.122724, 0.506901),
    (0.620005, 0.18384, 0.497524),
    (0.804752, 0.249911, 0.442102),
    (0.944006, 0.377643, 0.365136),
    (0.992196, 0.587502, 0.406299),
    (0.996369, 0.791167, 0.553499),
]
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
                self.axis[i].set_ylim(50, 1050)
                for entry in data[-SIZE:]:
                    # for entry in data:
                    xdata.append(entry.time)
                    ydata.append(entry.value)

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

    def init_dashboard(self) -> None:
        self.fig, self.axis = plt.subplots(MAX_CLIENTS)

    def show(self) -> None:
        anim = FuncAnimation(
            self.fig, self.animate, frames=np.array(list(range(40)))
        )
        suppress_warings(anim)
        plt.show()


def insert_data(database: Database) -> None:
    while True:
        sleep(5)
        data = Data(
            "test",
            datetime.now(),
            pack(int(random.random() * 900 + 100), 4),
        )
        database.insert(data, ("localhost", 8080))


def main() -> None:
    database = Database()
    interface = Interface(database)
    ins_data = Thread(target=insert_data, args=(database,))
    ins_data.start()
    interface.show()


if __name__ == "__main__":
    main()
