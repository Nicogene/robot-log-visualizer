import time
from datetime import datetime

import h5py
import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread
from threading import Lock

# Matplotlib class
from data_plotter.matplotlib_viewer_canvas import MatplotlibViewerCanvas


class Plotter(QThread):
    update_index = pyqtSignal()

    def __init__(self, initial_time, visualization_fps):
        QThread.__init__(self)

        # set device state
        self._state = 'pause'
        self.state_lock = Lock()

        # Index expressed in seconds
        self._index = 0
        self.index_lock = Lock()

        self.current_time = initial_time
        self.visualization_fps = visualization_fps
        self.mpl_canvas = None

    def assign_canvas(self, mpl_canvas: MatplotlibViewerCanvas):

        self.mpl_canvas = mpl_canvas

    def open_mat_file(self, file_name: str):

        with h5py.File(file_name, 'r') as f:

            # TODO: populate other dataset components
            com_position_measured = np.squeeze(np.array(f['robot_logger_device']['walking']['com']['position']['measured']['data']))
            self.mpl_canvas.set_com_position_measured(com_position_measured)

            timestamps = np.array(f['robot_logger_device']['walking']['com']['position']['measured']['timestamps'])
            initial_timestamp = np.array(f['robot_logger_device']['joints_state']['positions']['timestamps'])[0]
            timestamps = timestamps - initial_timestamp
            final_timestamp = np.array(f['robot_logger_device']['joints_state']['positions']['timestamps'])[-1] - initial_timestamp
            self.mpl_canvas.set_timestamps(timestamps, final_timestamp[0])

            self.index = 0

            # When loading the dataset, reconfigure the plot
            self.mpl_canvas.set_x_axis_len(self.mpl_canvas.final_timestamp)
            self.mpl_canvas.axes.set_xlabel("time [s]")
            self.mpl_canvas.axes.set_ylabel("value")
            self.mpl_canvas.draw()

    # Length in seconds
    def __len__(self):
        return int(self.mpl_canvas.final_timestamp)

    @property
    def state(self):
        self.state_lock.acquire()
        value = self._state
        self.state_lock.release()
        return value

    @state.setter
    def state(self, new_state):
        self.state_lock.acquire()
        self._state = new_state
        self.state_lock.release()

    @property
    def index(self):
        self.index_lock.acquire()
        value = self._index
        self.index_lock.release()
        return value

    @index.setter
    def index(self, index):
        self.index_lock.acquire()
        self._index = index
        self.index_lock.release()

    def register_update_index(self, slot):
        self.update_index.connect(slot)

    def run(self):

        while True:

            if self.state == 'running':

                # Clear and re-plot the figure
                self.mpl_canvas.axes.clear()
                self.mpl_canvas.plot_variable(self.mpl_canvas.com_position_measured_x)

                # Draw vertical line at current index
                self.mpl_canvas.axes.axvline(x=self.index)

                # Reconfigure and re-draw the plot
                self.mpl_canvas.set_x_axis_len(self.mpl_canvas.final_timestamp)
                self.mpl_canvas.axes.set_xlabel("time [s]")
                self.mpl_canvas.axes.set_ylabel("value")
                self.mpl_canvas.draw()

                self.index = self.index + 1/self.visualization_fps
                self.update_index.emit()

            self.synchronize()

    def synchronize(self):
        if self.current_time + 1/self.visualization_fps - datetime.now().timestamp() > 0:
            time.sleep(self.current_time + 1/self.visualization_fps - datetime.now().timestamp())
        else:
            # Debug to check whether the synchronization takes place or not
            print("no synch PLOTTER!")
        self.current_time = self.current_time + 1/self.visualization_fps





