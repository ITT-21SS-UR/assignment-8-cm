from enum import Enum

import pyqtgraph.flowchart.library as fclib
from PyQt5.QtCore import pyqtSignal, QObject
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

        self.__setup_gesture_state_selection_layout()
        self.__setup_gesture_button_layout()
        self.__setup_gesture_list()

        self.__connect_signals()

        self.setLayout(self.__layout)

    def __setup_gesture_state_selection_layout(self):
        self.__state_selection_layout = QtWidgets.QHBoxLayout()

        self.__setup_training_button()
        self.__setup_prediction_button()
        self.__setup_inactive_button()

        self.__layout.addLayout(self.__state_selection_layout)

    def __setup_training_button(self):
        self.__training_button = QtWidgets.QRadioButton(GestureNodeState.TRAINING.value)
        self.__training_button.clicked.connect(self.__training_button_clicked)
        self.__state_selection_layout.addWidget(self.__training_button)

    def __training_button_clicked(self):
        self.__gesture_model.set_gesture_state(GestureNodeState.TRAINING)

    def __setup_prediction_button(self):
        self.__prediction_button = QtWidgets.QRadioButton(GestureNodeState.PREDICTION.value)
        self.__prediction_button.clicked.connect(self.__prediction_button_clicked)
        self.__state_selection_layout.addWidget(self.__prediction_button)

    def __prediction_button_clicked(self):
        self.__gesture_model.set_gesture_state(GestureNodeState.PREDICTION)

    def __setup_inactive_button(self):
        self.__inactive_button = QtWidgets.QRadioButton(GestureNodeState.INACTIVE.value)
        self.__inactive_button.clicked.connect(self.__inactive_button_clicked)
        self.__inactive_button.setChecked(True)
        self.__state_selection_layout.addWidget(self.__inactive_button)

    def __inactive_button_clicked(self):  # TODO lambda for states?
        self.__gesture_model.set_gesture_state(GestureNodeState.INACTIVE)

    def __setup_gesture_button_layout(self):
        # TODO separate functions
        gesture_button_layout = QtWidgets.QVBoxLayout()
        self.__add_gesture_button = QtWidgets.QPushButton("Add gesture")
        self.__add_gesture_button.clicked.connect(self.__add_gesture_button_clicked)
        gesture_button_layout.addWidget(self.__add_gesture_button)

        self.__rename_gesture_button = QtWidgets.QPushButton("Rename gesture")
        self.__rename_gesture_button.clicked.connect(self.__rename_gesture_button_clicked)
        gesture_button_layout.addWidget(self.__rename_gesture_button)

        self.__retrain_gesture_button = QtWidgets.QPushButton("Retrain gesture")
        self.__retrain_gesture_button.clicked.connect(self.__retrain_gesture_button_clicked)
        gesture_button_layout.addWidget(self.__retrain_gesture_button)

        self.__remove_gesture_button = QtWidgets.QPushButton("Remove gesture")
        self.__remove_gesture_button.clicked.connect(self.__remove_gesture_button_clicked)
        gesture_button_layout.addWidget(self.__remove_gesture_button)

        self.__layout.addLayout(gesture_button_layout)

    def __add_gesture_button_clicked(self):
        gesture_name, ok = QtWidgets.QInputDialog.getText(self, "Add new gesture", "gesture name")

        if gesture_name:
            self.__gesture_model.add_gesture(gesture_name)

    def __is_gesture_item_selected(self):
        if self.__gesture_list.currentItem():
            return True

        return False

    def __show_no_gesture_item_selected(self):
        QtWidgets.QMessageBox.warning(self, "No Gesture selected", "No gesture name was selected")

    def __rename_gesture_button_clicked(self):
        if not self.__is_gesture_item_selected():
            self.__show_no_gesture_item_selected()
            return

        # do we need that?
        # TODO check if list item selected
        print("rename")
        gesture_name, ok = QtWidgets.QInputDialog.getText(self, "Rename gesture", "gesture name")

        if gesture_name:
            current_item = self.__gesture_list.currentItem()
            print(current_item)
            print(gesture_name)
            self.__gesture_model.rename_gesture(gesture_name)  # TODO

    def __retrain_gesture_button_clicked(self):
        if not self.__is_gesture_item_selected():
            self.__show_no_gesture_item_selected()
            return

        print("retrain")

    def __remove_gesture_button_clicked(self):
        if not self.__is_gesture_item_selected():
            self.__show_no_gesture_item_selected()
            return

        # TODO ask user if he really wants to delete this item

        selected_item = self.__gesture_list.currentItem()
        self.__gesture_model.remove_gesture(selected_item.text())

        self.__gesture_list.takeItem(self.__gesture_list.currentRow())

    def __setup_gesture_list(self):
        # TODO
        self.__gesture_list = QtWidgets.QListWidget()
        self.__layout.addWidget(self.__gesture_list)

    def __connect_signals(self):
        self.__gesture_model.gesture_item_added.connect(self.__add_gesture_item)
        self.__gesture_model.gesture_name_exists.connect(self.__show_gesture_name_exits)
        # TODO train, rename, delete

    def __add_gesture_item(self, gesture_name: str):
        gesture_item = QtWidgets.QListWidgetItem(gesture_name)
        self.__gesture_list.addItem(gesture_item)
        self.__gesture_list.setCurrentItem(gesture_item)

    def __show_gesture_name_exits(self, gesture_name: str):
        QtWidgets.QMessageBox.warning(self, "Gesture name exists",
                                      "Gesture name \"{}\" already exists (-_-)".format(gesture_name))


fclib.registerNodeType(GestureNode, [(NodeType.GESTURE.value,)])


class GestureNodeModel(QObject):
    GESTURE_NAME = "gesture_name"
    GESTURE_DATA = "gesture_data"

    gesture_item_added = pyqtSignal([str])
    gesture_name_exists = pyqtSignal([str])

    def __init__(self):
        super().__init__()
        self.__gestures = []

        self.__gesture_state = GestureNodeState.INACTIVE

    def __exists_gesture_name(self, gesture_name: str):
        for gesture in self.__gestures:
            if gesture_name in gesture[self.GESTURE_NAME]:
                return True

        return False

    def add_gesture(self, gesture_name: str):
        if self.__exists_gesture_name(gesture_name):
            self.gesture_name_exists.emit(gesture_name)
            return

        # TODO what should be stored as gesture data
        self.__gestures.append({self.GESTURE_NAME: gesture_name,
                                self.GESTURE_DATA: []})

        self.gesture_item_added.emit(gesture_name)

    def rename_gesture(self, old_name: str):
        # TODO is that necessary?
        # TODO check if name already exists
        # TODO check if oldname
        pass

    def train_gesture(self, gesture_name: str):
        pass

    def record_gesture(self, gesture_name: str):
        pass

    def predict_gesture(self, gesture_input):
        pass

    def remove_gesture(self, gesture_name: str):
        pass

    def set_gesture_state(self, state):
        self.__gesture_state = state
