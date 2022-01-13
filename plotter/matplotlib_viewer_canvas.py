# numpy
import numpy as np

# PyQt
from PyQt5 import QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# matplotilb
from matplotlib.figure import Figure
import matplotlib.animation as animation


class MatplotlibViewerCanvas(FigureCanvas):
    """
    Inherits from FigureCanvasQTAgg in order to integrate with PyQt.
    """

    def __init__(self, parent, animation_frame_rate):

        # create a new figure
        fig = Figure(dpi=100)

        # call FigureCanvas constructor
        FigureCanvas.__init__(self, fig)

        # set the parent of this FigureCanvas
        self.setParent(parent)

        # dataset components # TODO: extend to the other dataset components
        self.com_position_measured_x = np.array([])
        self.com_position_measured_y = np.array([])
        self.com_position_measured_z = np.array([])

        # setup the plot and the animations
        self.index = 0
        self.animation_frame_rate = animation_frame_rate
        self.setup_plot(fig)

    def setup_plot(self, figure):
        """
        Setup the main plot of the figure.
        """

        # add plot to the figure
        self.axes = figure.add_subplot()

        # set axes labels
        self.axes.set_xlabel("time [s]")
        self.axes.set_ylabel("value")

        # Define animations timestep
        time_step = 1.0 / self.animation_frame_rate * 1000

        # start the vertical line animation
        self.vertical_line, = self.axes.plot([], [], 'o-', lw=1, c='k')
        self.vertical_line_anim = animation.FuncAnimation(figure, self.update_vertical_line, interval=time_step, ) # TODO blit=True

        # TODO: extend to the other dataset components
        # start the com position animation
        self.walking_timestamps = np.array([])
        self.measured_com_x_line, = self.axes.plot([], [], lw=1, c='r')
        self.measured_com_y_line, = self.axes.plot([], [], lw=1, c='g')
        self.measured_com_z_line, = self.axes.plot([], [], lw=1, c='b')
        self.measured_com_anim = animation.FuncAnimation(figure, self.update_measured_com, interval=time_step, )  # TODO blit=True

    def update_index(self, index):
        self.index = index

    def update_vertical_line(self, frame_number):
        """
        Update the vertical line
        """

        # Draw vertical line at current index
        x = [self.index, self.index]
        y = [-1000, 1000]
        self.vertical_line.set_data(x, y)

    # TODO: make generic for all the data components
    def update_measured_com(self, frame_number):
        """
        Update the com plot
        """

        # Draw com components
        self.measured_com_x_line.set_data(self.walking_timestamps, self.com_position_measured_x)
        self.measured_com_y_line.set_data(self.walking_timestamps, self.com_position_measured_y)
        self.measured_com_z_line.set_data(self.walking_timestamps, self.com_position_measured_z)

        # TODO: Resize figure if plotted variables changed
        self.set_y_axis_limits(0,1.5)

    # TODO: add similar functions for the other dataset components
    def set_com_position_measured(self, com_position_measured):
        self.com_position_measured_x = com_position_measured[:, 0]
        self.com_position_measured_y = com_position_measured[:, 1]
        self.com_position_measured_z = com_position_measured[:, 2]

    def set_walking_timestamps(self, walking_timestamps):
        self.walking_timestamps = walking_timestamps

    def set_x_axis_len(self, len):
        self.axes.set_xlim(0, len)

    def set_y_axis_limits(self, lower_bound, upper_bound):
        self.axes.set_ylim(lower_bound, upper_bound)

