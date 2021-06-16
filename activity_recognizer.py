import sys

import pyqtgraph as pg
from PyQt5 import QtWidgets
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.flowchart import Flowchart

from DIPPID_pyqtnode import BufferNode, DIPPIDNode


# start program example:
# python3 activity_recognizer.py 5700
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
        # TODO

    def __setup_flowchart(self):
        self.__flow_chart = Flowchart(terminals={})
        self.__layout = QtGui.QGridLayout()
        self.__layout.addWidget(self.__flow_chart.widget(), 0, 0, 2, 1)

        self.__setup_dippid()
        # TODO

        self.setLayout(self.__layout)

    def __setup_dippid(self):
        # TODO
        self.__dippid_node = self.__flow_chart.createNode("DIPPID", pos=(0, 0))
        self.__dippid_node.set_port(self.__port_number)


def start_program():
    port_number = read_port_number()

    app = QtGui.QApplication([])
    main_window = MainWindow(port_number)
    main_window.show()

    if (sys.flags.interactive != 1) or not hasattr(QtCore, "PYQT_VERSION"):
        sys.exit(QtGui.QApplication.instance().exec_())

    sys.exit(app.exec_())


def read_port_number():
    if len(sys.argv) < 2:
        sys.stderr.write("Please give a port number as argument (-_-)\n")
        sys.exit(1)

    return sys.argv[1]


if __name__ == '__main__':
    start_program()
