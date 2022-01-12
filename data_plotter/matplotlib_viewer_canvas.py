# numpy
import numpy as np

# PyQt
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# matplotilb
from matplotlib.figure import Figure

class MatplotlibViewerCanvas(FigureCanvas):
    """
    Inherits from FigureCanvasQTAgg in order to integrate with PyQt.
    """
    def __init__(self, parent):
        
        # create a new figure
        fig = Figure(dpi = 100) # TODO: tune
        
        # call FigureCanvas constructor
        FigureCanvas.__init__(self, fig)

        # set the parent of this FigureCanvas
        self.setParent(parent)

        # dataset components # TODO: extend to the other dataset components
        self.com_position_measured_x = np.array([])
        self.com_position_measured_y = np.array([])
        self.com_position_measured_z = np.array([])

        self.timestamps = np.array([])
        self.final_timestamp = 0

        # setup the plot
        self.setup_plot(fig)

    def setup_plot(self, figure):
        """
        Setup the main plot of the figure.
        """

        # add plot to the figure
        self.axes = figure.add_subplot()

        # set labels
        self.axes.set_xlabel("time [s]")
        self.axes.set_ylabel("value")

    # TODO: add similar functions for the other dataset components
    def set_com_position_measured(self, com_position_measured):

        self.com_position_measured_x = com_position_measured[:, 0]
        self.com_position_measured_y = com_position_measured[:, 1]
        self.com_position_measured_z = com_position_measured[:, 2]

    def set_timestamps(self, timestamps, final_timestamp):

        self.timestamps = timestamps
        self.final_timestamp = final_timestamp

    def set_x_axis_len(self, len):

        self.axes.set_xlim(0,len)

    def plot_variable(self, variable):

        self.axes.plot(self.timestamps, variable)
