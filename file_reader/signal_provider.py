import time

import h5py
import numpy as np
from PyQt5.QtCore import pyqtSignal, QThread
from threading import Lock

# Matplotlib class
from plotter.matplotlib_viewer_canvas import MatplotlibViewerCanvas

class SignalProvider(QThread):
    update_index = pyqtSignal()

    def __init__(self, meshcat_visualizer):
        QThread.__init__(self)

        # set device state
        self._state = 'pause'
        self.state_lock = Lock()

        self._last_data = None

        self._index = 0
        self.index_lock = Lock()

        # Meshcat
        self.fps = 50
        self.meshcat_visualizer = meshcat_visualizer
        self.s = np.array([])
        self.robot_timestamps = np.array([])

        # Plotter
        self.mpl_canvas = None

    def assign_canvas(self, mpl_canvas: MatplotlibViewerCanvas):

        self.mpl_canvas = mpl_canvas

    def open_mat_file(self, file_name: str):

        with h5py.File(file_name, 'r') as f:

            self.index = 0

            # Meshcat
            self.s = np.squeeze(np.array(f['robot_logger_device']['joints_state']['positions']['data']))
            self.robot_timestamps = np.array(f['robot_logger_device']['joints_state']['positions']['timestamps'])
            initial_timestamp = self.robot_timestamps[0]
            self.robot_timestamps = self.robot_timestamps - initial_timestamp

            # Plotter
            # TODO: populate other dataset components
            com_position_measured = np.squeeze(np.array(f['robot_logger_device']['walking']['com']['position']['measured']['data']))
            self.mpl_canvas.set_com_position_measured(com_position_measured)

            walking_timestamps = np.array(f['robot_logger_device']['walking']['com']['position']['measured']['timestamps'])
            walking_timestamps = walking_timestamps - initial_timestamp
            self.mpl_canvas.set_walking_timestamps(walking_timestamps)

            # When loading the dataset, reconfigure the plot
            final_timestamp = self.robot_timestamps[-1]
            self.mpl_canvas.set_x_axis_len(final_timestamp)
            self.mpl_canvas.axes.set_xlabel("time [s]")
            self.mpl_canvas.axes.set_ylabel("value")
            self.mpl_canvas.draw()

    def __len__(self):
        return self.robot_timestamps.shape[0]

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

                temp_index = min(self.index, self.robot_timestamps.shape[0] - 1)

                # plots # TODO: update the plots based on the active variables

                # vertical line
                self.mpl_canvas.update_index(self.robot_timestamps[temp_index])

                # meshcat
                self._last_data = self.s[temp_index, :]
                R = np.eye(3)
                p = np.array([0.0, 0.0, 0.0])
                self.meshcat_visualizer.display(p, R, self._last_data)

                # update index
                self.index = self.index + int(100/self.fps)
                self.update_index.emit()

            time.sleep(1/self.fps)






