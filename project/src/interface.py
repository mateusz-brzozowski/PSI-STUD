from datetime import datetime, timedelta
from time import sleep
import random
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from database import Database
from data import Data

SIZE=10

x0 = [datetime.today() + timedelta(minutes=x) for x in range(40)]
y0=[random.randint(0, 10) for _ in range(40)]
x1 = [datetime.today() + timedelta(minutes=x) for x in range(40)]
y1=[random.randint(0, 10) for _ in range(40)]

class Interface:
    """
    Interfejs aplikacji:
    - może działać na oddzielnym wątku od pozostałych komponentów
    - aplikacja monitorująca
    - wyświetla aktualny stan bazy danych w postaci wykresów
    """
    database: Database

    def __init__(self, database, streams):
        self.database = database
        self.fig, self.axis = plt.subplots(streams)
        for i in range(streams):
            self.axis[i].set_title(f"Data source: {i}")
        self.xdata0, self.ydata0, self.xdata1, self.ydata1, self.xdata2, self.ydata2, self.xdata3, self.ydata3 = [], [], [], [], [], [], [], []
        self.xdata4, self.ydata4, self.xdata5, self.ydata5, self.xdata6, self.ydata6, self.xdata7, self.ydata7 = [], [], [], [], [], [], [], []

    def animate(self, i):
        self.xdata0.append(x0[i])
        self.ydata0.append(y0[i])
        self.xdata1.append(x1[i])
        self.ydata1.append(y1[i])
        self.axis[0].clear()
        self.axis[1].clear()
        self.axis[0].plot(self.xdata0[-SIZE:], self.ydata0[-SIZE:], 'r')
        self.axis[1].plot(self.xdata1[-SIZE:], self.ydata1[-SIZE:], 'b')

        sleep(1)
        #return 

    def show(self):
        ani = FuncAnimation(self.fig, self.animate, frames=np.array([x for x in range(0, 40)]))#,init_func=self.beginning)#, blit=True)
        plt.show()

def get_vals_from_key(key: str) -> list:
    stream_id, address, port = key.split(':')
    return [stream_id, address, port]

def title_with_address(key: str) -> str:
    address, port = get_vals_from_key(key)[1:]
    return f"Data source: {address}:{port}"

def main():
    # db = Database()
    # data1=Data()
    # db.insert()
    print(x0)
    sth = Interface("db_placeholder", 2)
    sth.show()

if __name__=="__main__":
    main()
