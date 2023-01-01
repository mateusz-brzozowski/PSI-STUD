from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from database import Database
from data import Data

X_LIM = (0, datetime.now()+timedelta(hours=1))
Y_LIM = (0, 50)

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
        self.ax1 = self.fig.add_subplot(1,1,1)
        keys=[1]*8
        #keys = database.keys()
        if len(keys) == 8:
            self.ax1.set_title(f"Data source: TODO")#{title_with_address(keys[0])}")
            self.xdata, self.ydata = [], []
            self.line0, = self.ax1.plot([], [], label='line0')#, label=f"{get_vals_from_key(keys[0])[0]}")     # 'o' for points
            self.line1, = self.ax1.plot([], [], label='line1')#, label=f"{get_vals_from_key(keys[1])[0]}")
            # self.line2, = self.ax1.plot([], [])
            # self.line3, = self.ax1.plot([], [])
            # self.line4, = self.ax1.plot([], [])
            # self.line5, = self.ax1.plot([], [])
            # self.line6, = self.ax1.plot([], [])
            # self.line7, = self.ax1.plot([], [])
        self.ax1.legend()


    def _update_view(self) -> None: pass

    def beginning(self):
        self.ax1.set_xlim(0, 2*np.pi)
        self.ax1.set_ylim(-1, 1)
        return self.line0, self.line1#, self.line2, self.line3, self.line4, self.line5, self.line6, self.line7,

    def animate(self, frame):
        self.xdata.append(frame)
        self.ydata.append(np.sin(frame))
        self.line0.set_data(self.xdata, self.ydata)
        self.line1.set_data(self.xdata, self.ydata)
        #ax1.plot(xdata, ydata)
        return self.line0, self.line1#, self.line2, self.line3, self.line4, self.line5, self.line6, self.line7,

    def show(self):
        ani = FuncAnimation(self.fig, self.animate, frames=np.linspace(0, 2*np.pi, 128),
                    init_func=self.beginning, blit=True)
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
    sth = Interface(2)
    sth.show()

if __name__=="__main__":
    main()
