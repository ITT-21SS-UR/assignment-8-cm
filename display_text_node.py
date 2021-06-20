import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtWidgets
from pyqtgraph.flowchart import Node

from node_constants import NodeKey


# DisplayTextNode that displays the latest predicted category on the screen.

# Author: Claudia
# Reviewer: Martina
class DisplayTextNode(Node):
    nodeName = "DisplayText"

    @staticmethod
    def get_node_name():
        return DisplayTextNode.nodeName

    def __init__(self, name):
        terminals = {
            NodeKey.PREDICTED_GESTURE.value: dict(io="in")
        }

        self.__display_text_widget = DisplayTextWidget()

        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwargs):
        # TODO change label text of predicted category in real time
        # predicted_category = kwargs[NodeKey.PREDICTED_CATEGORY.value][0]
        # print(predicted_category)
        # self.__display_text_widget.set_predicted_category_text(predicted_category)
        self.__display_text_widget.set_predicted_category_text("TODO")

    def ctrlWidget(self):
        return self.__display_text_widget


fclib.registerNodeType(DisplayTextNode, [(DisplayTextNode.get_node_name(),)])


class DisplayTextWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.__setup_layout()

    def __setup_layout(self):
        layout = QtWidgets.QVBoxLayout()

        # TODO current state
        self.__category_info = QtWidgets.QLabel()
        self.__category_info.setText("predicted gesture:")
        layout.addWidget(self.__category_info)

        self.__predicted_category = QtWidgets.QLabel()
        self.__predicted_category.setText("- no gesture detected -")
        layout.addWidget(self.__predicted_category)

        self.setLayout(layout)

    def set_predicted_category_text(self, predicted_category):
        self.__predicted_category.setText(predicted_category)
