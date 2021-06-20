import sys

import pyqtgraph as pg
from PyQt5 import QtWidgets
from pyqtgraph.Qt import QtCore
from pyqtgraph.flowchart import Flowchart

from DIPPID_pyqtnode import BufferNode, DIPPIDNode
from display_text_node import DisplayTextNode
from feature_extraction_filter_node import FeatureExtractionFilterNode
from gesture_node import GestureNode
from node_constants import NodeKey

"""
The workload was distributed evenly and tasks were discussed together.

# start program example:
# python3 activity_recognizer.py 5700

Errors like this are shown in the console that should be ignored. 
qt.qpa.xcb: QXcbConnection: XCB error: 3 (BadWindow), sequence: 973, resource id: 24177709, major code: 40 (TranslateCoords), minor code: 0
This is a known bug that sometimes occur when a dialog is closed (often happens when print is used).
https://bugreports.qt.io/browse/QTBUG-56893
"""


# Author: Claudia
# Reviewer: Martina
class MainWindow(QtWidgets.QWidget):

    def __init__(self, port_number=None):
        super(MainWindow, self).__init__()

        self.__port_number = port_number

        self.__setup_flowchart()
        self.__setup_main_window()

    def __setup_main_window(self):
        self.setWindowTitle("Activity Recognizer")
        self.move(QtWidgets.qApp.desktop().availableGeometry(
            self).center() - self.rect().center())
        # self.showMaximized()  # TODO when program finished

    def __setup_flowchart(self):
        self.__flow_chart = Flowchart(terminals={})
        self.__layout = QtWidgets.QGridLayout()
        self.__layout.addWidget(self.__flow_chart.widget(), 0, 0, 2, 1)

        self.__setup_dippid()
        self.__setup_buffers()
        self.__setup_feature_extraction_filter()
        self.__setup_gesture()
        self.__setup_display_text()

        self.setLayout(self.__layout)

    def __setup_dippid(self):
        self.__dippid_node = self.__flow_chart.createNode(DIPPIDNode.nodeName, pos=(-150, -80))
        self.__dippid_node.set_port(self.__port_number)

    def __setup_buffers(self):
        self.__setup_buffer_x()
        self.__setup_buffer_y()
        self.__setup_buffer_z()

    def __setup_buffer_x(self):
        self.__buffer_node_x = self.__flow_chart.createNode(BufferNode.nodeName, pos=(0, -100))
        self.__flow_chart.connectTerminals(self.__dippid_node[NodeKey.ACCEL_X.value],
                                           self.__buffer_node_x[NodeKey.DATA_IN.value])

    def __setup_buffer_y(self):
        self.__buffer_node_y = self.__flow_chart.createNode(BufferNode.nodeName, pos=(0, 0))
        self.__flow_chart.connectTerminals(self.__dippid_node[NodeKey.ACCEL_Y.value],
                                           self.__buffer_node_y[NodeKey.DATA_IN.value])

    def __setup_buffer_z(self):
        self.__buffer_node_z = self.__flow_chart.createNode(BufferNode.nodeName, pos=(0, 100))
        self.__flow_chart.connectTerminals(self.__dippid_node[NodeKey.ACCEL_Z.value],
                                           self.__buffer_node_z[NodeKey.DATA_IN.value])

    def __test_y_plot(self):
        # TODO remove after working spectrogram
        plot_time_signal = pg.PlotWidget()
        plot_time_signal.setTitle("test y accel")
        plot_time_signal.setYRange(-2, 2)
        self.__layout.addWidget(plot_time_signal, 1, 1)

        plot_time_signal_node = self.__flow_chart.createNode("PlotWidget", pos=(300, -100))
        plot_time_signal_node.setPlot(plot_time_signal)

        self.__flow_chart.connectTerminals(
            self.__buffer_node_y[NodeKey.DATA_OUT.value],
            plot_time_signal_node["In"]
        )

    def __setup_feature_extraction_filter(self):
        # TODO separate functions  self.__setup_spectrogram_x()
        # TODO plot for time signal?
        # plot_time_signal = pg.PlotWidget()
        # plot_time_signal.setTitle("time signal/accel x")
        # plot_time_signal.setYRange(-4, 4)
        # self.__layout.addWidget(plot_time_signal, 0, 1)
        #
        # plot_time_signal_node = self.__flow_chart.createNode("PlotWidget", pos=(300, -100))
        # plot_time_signal_node.setPlot(plot_time_signal)

        # TODO show spectrogram_x
        plot_spectrogram_x = pg.PlotWidget()
        plot_spectrogram_x.setTitle("spectrogram x")
        plot_spectrogram_x.setYRange(-4, 4)  # TODO range
        self.__layout.addWidget(plot_spectrogram_x, 0, 1)
        # what are the axis "Frequency [Hz]" "Time [sec]" "Amplitude" "Intensity"

        plot_spectrogram_node_x = self.__flow_chart.createNode("PlotWidget", pos=(300, -50))
        plot_spectrogram_node_x.setPlot(plot_spectrogram_x)

        self.__feature_extraction_filter_node = self.__flow_chart.createNode(
            FeatureExtractionFilterNode.get_node_name(),
            pos=(150, -75))

        # buffer node usage is slower than directly using the dippid node
        # TODO move to coressponding spectrogram function
        self.__flow_chart.connectTerminals(self.__buffer_node_x[NodeKey.DATA_OUT.value],
                                           # self.__dippid_node["accelX"],
                                           # self.__feature_extraction_filter_node["accelX"])
                                           self.__feature_extraction_filter_node[NodeKey.ACCEL_X.value])
        self.__flow_chart.connectTerminals(self.__buffer_node_y[NodeKey.DATA_OUT.value],
                                           # self.__dippid_node["accelY"],
                                           self.__feature_extraction_filter_node[NodeKey.ACCEL_Y.value])
        self.__flow_chart.connectTerminals(self.__buffer_node_z[NodeKey.DATA_OUT.value],
                                           # self.__dippid_node["accelZ"],
                                           self.__feature_extraction_filter_node[NodeKey.ACCEL_Z.value])

        # TODO remove this connection
        self.__test_y_plot()

        # TODO time signal connection
        # self.__flow_chart.connectTerminals(
        #     self.__feature_extraction_filter_node[NodeKey.TIME_SIGNAL_X.value],
        #     plot_time_signal_node["In"]
        # )

        # TODO NodeKey.FFT.value at certain position

        # TODO spectrogram_x connection
        self.__flow_chart.connectTerminals(
            self.__feature_extraction_filter_node[NodeKey.SPECTROGRAM_X.value],
            plot_spectrogram_node_x["In"]
        )

    def __setup_spectrogram_y(self):
        plot_spectrogram_y = pg.PlotWidget()
        plot_spectrogram_y.setTitle("spectrogram y")
        plot_spectrogram_y.setYRange(-2, 2)

        plot_spectrogram_node_y = self.__flow_chart.createNode("PlotWidget", pos=(300, -100))
        plot_spectrogram_node_y.setPlot(plot_spectrogram_y)
        self.__layout.addWidget(plot_spectrogram_y, 2, 1)

        self.spectrogram_node_y = self.__flow_chart.createNode(
            FeatureExtractionFilterNode.get_node_name(),
            pos=(150, -75))

        self.__flow_chart.connectTerminals(
            # self.__dippid_node[NodeInputOutputType.ACCEL_Y.value], # this is not working
            self.__buffer_node_y[NodeKey.DATA_OUT.value],
            plot_spectrogram_node_y["In"]
        )

    def __setup_spectrogram_x(self):
        # TODO spectrogram for x
        pass

    def __setup_spectrogram_z(self):
        # TODO spectrogram for z
        pass

    def __setup_gesture(self):
        self.__gesture_node = self.__flow_chart.createNode(GestureNode.get_node_name(), pos=(150, 50))

        # TODO output
        #  self.__flow_chart.connectTerminals(self.__feature_extraction_filter_node["FREQUENCY_SPECTROGRAM"],
        #                                   self.__activity_recognition_node[
        #                                       NodeInputOutputType.sample.value])

    def __setup_display_text(self):
        self.__display_text_node = self.__flow_chart.createNode(DisplayTextNode.get_node_name(), pos=(150, 100))

        # TODO get predicted category text
        # self.__flow_chart.connectTerminals(self.__buffer_node_y[NodeKey.DATA_OUT.value],
        #                                    self.__display_text_node[NodeKey.PREDICTED_CATEGORY.value])

        self.__flow_chart.connectTerminals(self.__feature_extraction_filter_node[NodeKey.FFT.value],
                                           self.__display_text_node[NodeKey.PREDICTED_CATEGORY.value])


def start_program():
    port_number = read_port_number()

    app = QtWidgets.QApplication([])
    main_window = MainWindow(port_number)
    main_window.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
        sys.exit(QtWidgets.QApplication.instance().exec_())

    sys.exit(app.exec_())


def read_port_number():
    if len(sys.argv) < 2:
        sys.stderr.write("Please give a port number as argument (￢_￢)\n")
        # sys.exit(1) # TODO uncomment
        return 5700

    return sys.argv[1]


if __name__ == '__main__':
    start_program()
