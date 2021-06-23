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

Usually the code (e.g. function and variable names) already describes
what the code does (code is self-explanatory) so there are only some comments.

# start program example:
# python3 activity_recognizer.py 5700

MainWindow is responsible for the main application like setting the flowchart, nodes and their connections.

Errors like this are shown in the console that should be ignored:
qt.qpa.xcb: QXcbConnection: XCB error: 3 (BadWindow), sequence: 973, resource id: 24177709,
major code: 40 (TranslateCoords), minor code: 0

This is a known bug that sometimes occurs when e.g. a dialog is closed.
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
        self.setMinimumSize(1000, 700)

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

    def __setup_feature_extraction_filter(self):
        self.__feature_extraction_filter_node = self.__flow_chart.createNode(
            FeatureExtractionFilterNode.get_node_name(),
            pos=(150, -75))

        self.__flow_chart.connectTerminals(self.__buffer_node_x[NodeKey.DATA_OUT.value],
                                           self.__feature_extraction_filter_node[NodeKey.ACCEL_X.value])
        self.__flow_chart.connectTerminals(self.__buffer_node_y[NodeKey.DATA_OUT.value],
                                           self.__feature_extraction_filter_node[NodeKey.ACCEL_Y.value])
        self.__flow_chart.connectTerminals(self.__buffer_node_z[NodeKey.DATA_OUT.value],
                                           self.__feature_extraction_filter_node[NodeKey.ACCEL_Z.value])

        self.__setup_spectrogram()

    def __setup_spectrogram(self):
        plot_spectrogram = pg.PlotWidget()
        plot_spectrogram.setTitle("spectrogram average")
        plot_spectrogram.setYRange(0, 2)
        plot_spectrogram.setXRange(0, 14)
        self.__layout.addWidget(plot_spectrogram, 0, 1)

        plot_spectrogram_node = self.__flow_chart.createNode("PlotWidget", pos=(300, -100))
        plot_spectrogram_node.setPlot(plot_spectrogram)

        self.__flow_chart.connectTerminals(
            self.__feature_extraction_filter_node[NodeKey.SPECTROGRAM_AVG.value],
            plot_spectrogram_node["In"])

    def __setup_gesture(self):
        self.__gesture_node = self.__flow_chart.createNode(GestureNode.get_node_name(), pos=(200, 50))

        self.__flow_chart.connectTerminals(self.__feature_extraction_filter_node[NodeKey.FFT.value],
                                           self.__gesture_node[NodeKey.GESTURE_DATA.value])

    def __setup_display_text(self):
        self.__display_text_node = self.__flow_chart.createNode(DisplayTextNode.get_node_name(), pos=(300, 100))

        self.__flow_chart.connectTerminals(self.__gesture_node[NodeKey.PREDICTED_GESTURE.value],
                                           self.__display_text_node[NodeKey.TEXT.value])


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
        print("Port number is set to 5700. (￢_￢)")
        return 5700

    return sys.argv[1]


if __name__ == '__main__':
    start_program()
