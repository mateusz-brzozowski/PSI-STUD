import random
from datetime import datetime, timedelta
from time import sleep

import matplotlib.pyplot as plt  # type: ignore
import numpy as np

# from data import Data
from database import Database
from matplotlib.animation import FuncAnimation  # type: ignore

X_LIM = (0, datetime.now() + timedelta(hours=1))
Y_LIM = (0, 50)
SIZE = 20

working_x_lim = datetime.now(), datetime.now() + timedelta(minutes=5)
x0 = [datetime.now() + timedelta(minutes=x) for x in range(40)]
working_y_lim = (0, 10)
y0 = [random.randint(0, 10) for _ in range(40)]
x1 = [datetime.now() + timedelta(minutes=x) for x in range(40)]
y1 = [random.randint(0, 10) for _ in range(40)]


class Interface:
    """
    Interfejs aplikacji:
    - może działać na oddzielnym wątku od pozostałych komponentów
    - aplikacja monitorująca
    - wyświetla aktualny stan bazy danych w postaci wykresów
    """

    database: Database

    def __init__(self, database):
        self.database = database
        self.fig = plt.figure()
        self.ax1 = self.fig.add_subplot(1, 1, 1)
        keys = [1] * 8
        # keys = database.keys()
        if len(keys) == 8:
            self.ax1.set_title(
                "Data source: TODO"
            )  # {title_with_address(keys[0])}")
            (self.line0,) = self.ax1.plot(
                [], [], label="line0"
            )  # , label=f"{get_vals_from_key(keys[0])[0]}")     # 'o' for points
            (self.line1,) = self.ax1.plot(
                [], [], label="line1"
            )  # , label=f"{get_vals_from_key(keys[1])[0]}")
            (self.line2,) = self.ax1.plot([], [], label="line2")
            (self.line3,) = self.ax1.plot([], [], label="line3")
            (self.line4,) = self.ax1.plot([], [], label="line4")
            (self.line5,) = self.ax1.plot([], [], label="line5")
            (self.line6,) = self.ax1.plot([], [], label="line6")
            (self.line7,) = self.ax1.plot([], [], label="line7")
        self.ax1.legend()

    def beginning(self):
        self.ax1.set_xlim(working_x_lim)
        self.ax1.set_ylim(working_y_lim)
        (
            self.xdata0,
            self.ydata0,
            self.xdata1,
            self.ydata1,
            self.xdata2,
            self.ydata2,
            self.xdata3,
            self.ydata3,
        ) = ([], [], [], [], [], [], [], [])
        (
            self.xdata4,
            self.ydata4,
            self.xdata5,
            self.ydata5,
            self.xdata6,
            self.ydata6,
            self.xdata7,
            self.ydata7,
        ) = ([], [], [], [], [], [], [], [])
        return (
            self.line0,
            self.line1,
            self.line2,
            self.line3,
            self.line4,
            self.line5,
            self.line6,
            self.line7,
        )

    def animate(self, i):
        self.xdata0.append(x0[i])
        self.ydata0.append(y0[i])
        self.xdata1.append(x1[i])
        self.ydata1.append(y1[i])
        self.line0.set_data(self.xdata0[-SIZE:], self.ydata0[-SIZE:])
        self.line1.set_data(self.xdata1[-SIZE:], self.ydata1[-SIZE:])
        self.ax1.set_xlim(min(self.xdata0), max(self.xdata0))
        sleep(1)
        return (
            self.line0,
            self.line1,
            self.line2,
            self.line3,
            self.line4,
            self.line5,
            self.line6,
            self.line7,
        )

    def show(self):
        ani = FuncAnimation(
            self.fig,
            self.animate,
            frames=np.array(list(range(40))),
            init_func=self.beginning,
        )  # , blit=True)
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
    print(x0)
    sth = Interface(2)
    sth.show()


if __name__ == "__main__":
    main()
