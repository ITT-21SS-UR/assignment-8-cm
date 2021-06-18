from enum import Enum

import pyqtgraph.flowchart.library as fclib
from pyqtgraph.Qt import QtWidgets
from pyqtgraph.flowchart import Node

from node_constants import NodeType, NodeInputOutputType


class GestureNodeState(Enum):
    TRAINING = "training"
    PREDICTION = "prediction"
    INACTIVE = "inactive"


class GestureNode(Node):
    nodeName = NodeType.GESTURE.value

    def __init__(self, name):
        terminals = {
            # TODO
            NodeInputOutputType.SAMPLE.value: dict(io="in"),
            NodeInputOutputType.PREDICTED_CATEGORY.value: dict(io="out")
        }

        self.__gesture_node_widget = GestureNodeWidget()

        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwargs):
        # TODO
        pass

    def ctrlWidget(self):
        return self.__gesture_node_widget


class GestureNodeWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.__gesture_model = GestureNodeModel()
        self.__setup_layout()

    def __setup_layout(self):
        self.__layout = QtWidgets.QVBoxLayout()

        self.__setup_state_selection_layout()
        # TODO more

        self.setLayout(self.__layout)

    def __setup_state_selection_layout(self):
        self.__state_selection_layout = QtWidgets.QHBoxLayout()

        self.__setup_training_button()
        self.__setup_prediction_button()
        self.__setup_inactive_button()

        self.__layout.addLayout(self.__state_selection_layout)

    def __setup_training_button(self):
        self.__training_button = QtWidgets.QRadioButton(GestureNodeState.TRAINING.value)
        self.__training_button.clicked.connect(self.__on_training_button_clicked)

        self.__state_selection_layout.addWidget(self.__training_button)

    def __on_training_button_clicked(self):
        print("train")

    def __setup_prediction_button(self):
        self.__prediction_button = QtWidgets.QRadioButton(GestureNodeState.PREDICTION.value)
        self.__prediction_button.clicked.connect(self.__on_prediction_button_clicked)

        self.__state_selection_layout.addWidget(self.__prediction_button)

    def __on_prediction_button_clicked(self):
        print("predict")

    def __setup_inactive_button(self):
        self.__inactive_button = QtWidgets.QRadioButton(GestureNodeState.INACTIVE.value)
        self.__inactive_button.clicked.connect(self.__on_inactive_button_clicked)
        self.__inactive_button.setChecked(True)

        self.__state_selection_layout.addWidget(self.__inactive_button)

    def __on_inactive_button_clicked(self):
        print("inactive")


fclib.registerNodeType(GestureNode, [(NodeType.GESTURE.value,)])


class GestureNodeModel:
    def __init__(self):
        self.__gestures = {}

        self.__gesture_state = GestureNodeState.INACTIVE
