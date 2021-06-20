from enum import Enum

import pyqtgraph.flowchart.library as fclib
from PyQt5.QtCore import pyqtSignal, QObject
from pyqtgraph.Qt import QtWidgets
from pyqtgraph.flowchart import Node
from sklearn import svm

from node_constants import NodeKey


# Author: Claudia
# Reviewer: Martina
class GestureNodeState(Enum):
    TRAINING = "training"
    PREDICTION = "prediction"
    INACTIVE = "inactive"


class GestureNode(Node):
    nodeName = "Gesture"

    @staticmethod
    def get_node_name():
        return GestureNode.nodeName

    def __init__(self, name):
        terminals = {
            # TODO
            NodeKey.SAMPLE.value: dict(io="in"),
            NodeKey.PREDICTED_CATEGORY.value: dict(io="out")
        }

        self.__gesture_node_widget = GestureNodeWidget()

        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwargs):
        # TODO process kwargs
        gesture_state = self.__gesture_node_widget.get_gesture_model().get_gesture_state()
        if gesture_state == GestureNodeState.TRAINING:
            pass
        elif gesture_state == GestureNodeState.PREDICTION:
            pass
        elif gesture_state == GestureNodeState.INACTIVE:
            pass

    def ctrlWidget(self):
        return self.__gesture_node_widget


fclib.registerNodeType(GestureNode, [(GestureNode.nodeName,)])


class GestureNodeWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.__gesture_model = GestureNodeModel()
        self.__setup_layout()
        self.__classifier = svm.SVC()  # TODO which type?

    def __setup_layout(self):
        self.__layout = QtWidgets.QVBoxLayout()

        self.__setup_gesture_state_selection_layout()
        self.__setup_gesture_button_layout()
        self.__setup_gesture_list()

        self.__connect_signals()

        self.setLayout(self.__layout)

    def __setup_gesture_state_selection_layout(self):
        self.__state_selection_layout = QtWidgets.QVBoxLayout()

        self.__setup_training_button()
        self.__setup_prediction_button()
        self.__setup_inactive_button()

        self.__layout.addLayout(self.__state_selection_layout)

    def __setup_training_button(self):
        self.__training_button = QtWidgets.QRadioButton(GestureNodeState.TRAINING.value)
        self.__training_button.clicked.connect(self.__training_button_clicked)
        self.__state_selection_layout.addWidget(self.__training_button)

    def __training_button_clicked(self):  # TODO states
        self.__training_button.setChecked(True)
        self.__gesture_model.set_gesture_state(GestureNodeState.TRAINING)

    def __setup_prediction_button(self):
        self.__prediction_button = QtWidgets.QRadioButton(GestureNodeState.PREDICTION.value)
        self.__prediction_button.clicked.connect(self.__prediction_button_clicked)
        self.__state_selection_layout.addWidget(self.__prediction_button)

    def __prediction_button_clicked(self):  # TODO states
        self.__gesture_model.set_gesture_state(GestureNodeState.PREDICTION)

    def __setup_inactive_button(self):
        self.__inactive_button = QtWidgets.QRadioButton(GestureNodeState.INACTIVE.value)
        self.__inactive_button.clicked.connect(self.__inactive_button_clicked)
        self.__inactive_button.setChecked(True)
        self.__state_selection_layout.addWidget(self.__inactive_button)

    def __inactive_button_clicked(self):  # TODO lambda for states?
        self.__gesture_model.set_gesture_state(GestureNodeState.INACTIVE)

    def __setup_gesture_button_layout(self):
        self.__gesture_button_layout = QtWidgets.QVBoxLayout()

        self.__setup_add_gesture()
        self.__setup_retrain_gesture()
        self.__setup_remove_gesture()

        self.__layout.addLayout(self.__gesture_button_layout)

    def __setup_add_gesture(self):
        self.__add_gesture_button = QtWidgets.QPushButton("Add gesture")
        self.__add_gesture_button.clicked.connect(self.__add_gesture_button_clicked)
        self.__gesture_button_layout.addWidget(self.__add_gesture_button)

    def __add_gesture_button_clicked(self):
        gesture_name, ok = QtWidgets.QInputDialog.getText(self, "Add new gesture", "gesture name")

        if gesture_name:
            self.__gesture_model.add_gesture(gesture_name)

    def __is_gesture_item_selected(self):
        if self.__gesture_list.currentItem():
            return True

        return False

    def __show_no_gesture_item_selected(self):
        QtWidgets.QMessageBox.warning(self, "No gesture selected", "No gesture was selected")

    def __setup_retrain_gesture(self):
        self.__retrain_gesture_button = QtWidgets.QPushButton("Retrain gesture")
        self.__retrain_gesture_button.clicked.connect(self.__retrain_gesture_button_clicked)
        self.__gesture_button_layout.addWidget(self.__retrain_gesture_button)

    def __retrain_gesture_button_clicked(self):
        if not self.__is_gesture_item_selected():
            self.__show_no_gesture_item_selected()
            return

        self.__show_gesture_confirm_retrain()

    def __setup_remove_gesture(self):
        self.__remove_gesture_button = QtWidgets.QPushButton("Remove gesture")
        self.__remove_gesture_button.clicked.connect(self.__remove_gesture_button_clicked)
        self.__gesture_button_layout.addWidget(self.__remove_gesture_button)

    def __remove_gesture_button_clicked(self):
        if not self.__is_gesture_item_selected():
            self.__show_no_gesture_item_selected()
            return

        self.__show_gesture_confirm_removal()

    def __setup_gesture_list(self):
        gesture_label = QtWidgets.QLabel()
        gesture_label.setText("\nGestures")
        self.__layout.addWidget(gesture_label)

        self.__gesture_list = QtWidgets.QListWidget()
        self.__layout.addWidget(self.__gesture_list)

    def __connect_signals(self):
        self.__gesture_model.gesture_name_exists.connect(self.__show_gesture_name_exits)
        self.__gesture_model.gesture_item_added.connect(self.__add_gesture_item)

        # TODO train, predict?

    def __add_gesture_item(self, gesture_name: str):
        gesture_item = QtWidgets.QListWidgetItem(gesture_name)
        self.__gesture_list.addItem(gesture_item)
        self.__gesture_list.setCurrentItem(gesture_item)

    def __show_gesture_name_exits(self, gesture_name: str):
        QtWidgets.QMessageBox.warning(self, "Gesture exists",
                                      "Gesture \"{}\" already exists. (-_-)".format(gesture_name))

    def __show_gesture_confirm_removal(self):
        gesture_name = self.__gesture_list.currentItem().text()

        remove_reply = QtWidgets.QMessageBox.question(self, "Remove gesture", "Are you sure to remove gesture \"{}\".\n"
                                                                              "This action can't be undone."
                                                      .format(gesture_name))

        if remove_reply == QtWidgets.QMessageBox.Yes:
            self.__gesture_model.remove_gesture(gesture_name)
            self.__gesture_list.takeItem(self.__gesture_list.currentRow())

    def __show_gesture_confirm_retrain(self):
        gesture_name = self.__gesture_list.currentItem().text()

        retrain_reply = QtWidgets.QMessageBox.question(self, "Retrain gesture",
                                                       "Are you sure to retrain gesture \"{}\".\n"
                                                       "All trained data of this gesture will be removed.\n"
                                                       "This action can't be undone."
                                                       .format(gesture_name))

        if retrain_reply == QtWidgets.QMessageBox.Yes:
            self.__gesture_model.retrain_gesture(gesture_name)
            self.__training_button_clicked()

    def get_gesture_model(self):
        return self.__gesture_model


class GestureNodeModel(QObject):
    GESTURE_NAME = "gesture_name"
    GESTURE_DATA = "gesture_data"

    state_changed = pyqtSignal([str])
    gesture_name_exists = pyqtSignal([str])
    gesture_item_added = pyqtSignal([str])
    record_changed = pyqtSignal([bool])

    def __init__(self):
        super().__init__()
        self.__gestures = []
        self.__setup_pretrained_gestures()
        self.__gesture_state = GestureNodeState.INACTIVE

    def __setup_pretrained_gestures(self):
        # TODO setup pretrained gestures: use csv hop stand walk from data folder
        pass

    def __exists_gesture_name(self, gesture_name: str):
        for gesture in self.__gestures:
            if gesture_name in gesture[self.GESTURE_NAME]:
                return True

        return False

    def __find_gesture_by_name(self, gesture_name):
        return next((gesture for gesture in self.__gestures if gesture[self.GESTURE_NAME] == gesture_name), None)

    def add_gesture(self, gesture_name: str):
        if self.__exists_gesture_name(gesture_name):
            self.gesture_name_exists.emit(gesture_name)
            return

        # TODO what should be stored as gesture data (format)
        self.__gestures.append({self.GESTURE_NAME: gesture_name,
                                self.GESTURE_DATA: []})

        self.gesture_item_added.emit(gesture_name)

    def record_gesture(self, gesture_name: str):
        pass

    def train_gesture(self, gesture_name: str):
        # TODO train gesture
        selected_gesture = self.__find_gesture_by_name(gesture_name)
        print(selected_gesture)
        # label
        # Click button to start training. Click again to stop the training.
        # Training ...

        # Push button
        # Begin training
        # Stop training

        pass

    def retrain_gesture(self, gesture_name: str):
        # TODO
        print("retrain: {}".format(gesture_name))
        gesture = self.__find_gesture_by_name(gesture_name)
        gesture[self.GESTURE_DATA] = []  # clear training data  TODO which (format)
        self.train_gesture(gesture_name)

    def predict_gesture(self, gesture_input):
        # TODO predict_gesture
        # label predicted gesture:
        # name of predicted gesture min requirement 1 gesture to start prediction
        # classifier.fit(samples, c1)  # TODO for training
        # u_class = classifier.predict([[xu, yu]])
        # print(u_class)

        pass

    def remove_gesture(self, gesture_name: str):
        self.__gestures = [item for item in self.__gestures if not (item[self.GESTURE_NAME] == gesture_name)]

    def get_gesture_state(self):
        return self.__gesture_state

    def set_gesture_state(self, state):
        self.__gesture_state = state


class GestureItemData:
    # TODO GestureItemData?
    pass
