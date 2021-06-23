from enum import Enum

import pyqtgraph.flowchart.library as fclib
from PyQt5.QtCore import pyqtSignal, QObject
from pyqtgraph.Qt import QtWidgets
from pyqtgraph.flowchart import Node
from sklearn import svm
from sklearn.exceptions import NotFittedError

from node_constants import NodeKey

"""
GestureNode that outputs the latest predicted gesture, state or an error as a dict with a string.
    Processes input data depending on the state of the model and returns the relevant text.

GestureNodeWidget is responsible for the UI of the GestureNode.
    Is used for layout components and its UI changes e.g. setting, connecting signals to button clicks
    so that the model can handle them.

GestureNodeModel saves and processes relevant data for the GestureNodeWidget and GestureNode.
    Is used to add, remove, predict, retrain, train gestures and to collect training data.
    Emits signals when a layout element should be changed. E.g. when a user removes a gesture.

Gestures that are good for prediction:
    - stand still
    - hop
    - shake

There was no requirement that the gestures have to be pre trained so the user has to train them themselves.
They are only added with empty training data so that they don't have to be added manually.
"""


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
            NodeKey.GESTURE_DATA.value: dict(io="in"),
            NodeKey.PREDICTED_GESTURE.value: dict(io="out")
        }

        self.__gesture_node_widget = GestureNodeWidget()

        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwargs):
        gesture_model = self.__gesture_node_widget.get_gesture_model()
        gesture_state = gesture_model.get_gesture_state()

        if gesture_state == GestureNodeState.TRAINING:
            gesture_model.collect_training_data(kwargs)
            gesture_output = "training state"

        elif gesture_state == GestureNodeState.PREDICTION:
            gesture_output = gesture_model.predict_gesture(kwargs)

        else:
            gesture_output = "inactive state"

        return {NodeKey.PREDICTED_GESTURE.value: gesture_output}

    def ctrlWidget(self):
        return self.__gesture_node_widget


fclib.registerNodeType(GestureNode, [(GestureNode.nodeName,)])


class GestureNodeWidget(QtWidgets.QWidget):
    BEGIN_TRAINING_TEXT = "Begin Training"
    TRAINING_TEXT = "Training..."

    def __init__(self):
        super().__init__()

        self.__gesture_model = GestureNodeModel()
        self.__setup_layout()
        self.__gesture_model.setup_pre_added_gestures()

    def __setup_layout(self):
        self.__layout = QtWidgets.QVBoxLayout()

        self.__setup_gesture_state_selection_layout()
        self.__setup_gesture_button_layout()
        self.__setup_info_text()
        self.__setup_training_button()
        self.__setup_gesture_list()

        # was added here because the training button should appear after the info text
        # so that no error occurs when the training button is hidden/shown
        self.__handle_state_changed(self.__gesture_model.get_gesture_state())

        self.__connect_signals()
        self.setLayout(self.__layout)

    def __setup_gesture_state_selection_layout(self):
        self.__state_selection_layout = QtWidgets.QVBoxLayout()

        self.__setup_state_label()
        self.__setup_inactive_button()
        self.__setup_select_training_button()
        self.__setup_prediction_button()

        self.__layout.addLayout(self.__state_selection_layout)

    def __setup_state_label(self):
        state_label = QtWidgets.QLabel()
        state_label.setText("State")
        self.__state_selection_layout.addWidget(state_label)

    def __setup_select_training_button(self):
        self.__select_training_button = QtWidgets.QRadioButton(GestureNodeState.TRAINING.value)
        self.__select_training_button.clicked.connect(self.__select_training_button_clicked)
        self.__state_selection_layout.addWidget(self.__select_training_button)

    def __select_training_button_clicked(self):
        self.__select_training_button.setChecked(True)
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

    def __inactive_button_clicked(self):
        self.__gesture_model.set_gesture_state(GestureNodeState.INACTIVE)

    def __setup_gesture_button_layout(self):
        self.__gesture_button_layout = QtWidgets.QVBoxLayout()

        self.__setup_add_gesture()
        self.__setup_retrain_gesture()
        self.__setup_remove_gesture()

        self.__layout.addLayout(self.__gesture_button_layout)

    def __setup_info_text(self):
        self.__info_text = QtWidgets.QLabel()
        self.__info_text.setWordWrap(True)
        self.__layout.addWidget(self.__info_text)

    def __handle_state_changed(self, state):
        self.__handle_stop_training()

        if state == GestureNodeState.TRAINING:
            self.__info_text.setText("To train your gesture click \"{}\".\n"
                                     "Click on \"{}\" to stop the training.".format(self.BEGIN_TRAINING_TEXT,
                                                                                    self.TRAINING_TEXT))
            self.__training_button.show()

        elif state == GestureNodeState.PREDICTION:
            self.__info_text.setText("Predicted gesture is shown in DisplayText.\n"
                                     "A minimum of 2 trained gestures is required for correct prediction.")
            self.__training_button.hide()

        elif state == GestureNodeState.INACTIVE:
            self.__info_text.setText("Select another state to train or predict a gesture.")
            self.__training_button.hide()

    def __handle_stop_training(self):
        self.__training_button.setText(self.BEGIN_TRAINING_TEXT)
        self.__gesture_model.train_gestures()

    def __setup_training_button(self):
        self.__training_button = QtWidgets.QPushButton()
        self.__training_button.setText(self.BEGIN_TRAINING_TEXT)
        self.__training_button.clicked.connect(self.__training_button_clicked)
        self.__layout.addWidget(self.__training_button)

    def __training_button_clicked(self):
        if self.__gesture_model.is_training():
            self.__handle_stop_training()
        else:
            if self.__gesture_model.is_gestures_empty():
                self.__show_no_gesture_item_selected()
                return

            self.__training_button.setText(self.TRAINING_TEXT)
            self.__gesture_model.set_is_training(True)

    def __setup_add_gesture(self):
        self.__add_gesture_button = QtWidgets.QPushButton("Add gesture")
        self.__add_gesture_button.clicked.connect(self.__add_gesture_button_clicked)
        self.__gesture_button_layout.addWidget(self.__add_gesture_button)

    def __add_gesture_button_clicked(self):
        self.__handle_stop_training()
        gesture_name, ok = QtWidgets.QInputDialog.getText(self, "Add new gesture", "new gesture name")

        if gesture_name:
            self.__gesture_model.add_gesture(gesture_name)

    def __is_gesture_item_selected(self):
        if self.__gesture_list.currentItem():
            return True

        return False

    def __show_no_gesture_item_selected(self):
        QtWidgets.QMessageBox.warning(self, "No gesture selected", "No gesture was selected.\n"
                                                                   "Please select or add a gesture.")

    def __setup_retrain_gesture(self):
        self.__retrain_gesture_button = QtWidgets.QPushButton("Retrain gesture")
        self.__retrain_gesture_button.clicked.connect(self.__retrain_gesture_button_clicked)
        self.__gesture_button_layout.addWidget(self.__retrain_gesture_button)

    def __retrain_gesture_button_clicked(self):
        self.__handle_stop_training()

        if not self.__is_gesture_item_selected():
            self.__show_no_gesture_item_selected()
            return

        self.__show_gesture_accept_retrain()

    def __setup_remove_gesture(self):
        self.__remove_gesture_button = QtWidgets.QPushButton("Remove gesture")
        self.__remove_gesture_button.clicked.connect(self.__remove_gesture_button_clicked)
        self.__gesture_button_layout.addWidget(self.__remove_gesture_button)

    def __remove_gesture_button_clicked(self):
        self.__handle_stop_training()

        if not self.__is_gesture_item_selected():
            self.__show_no_gesture_item_selected()
            return

        self.__show_gesture_accept_removal()

    def __setup_gesture_list(self):
        gesture_label = QtWidgets.QLabel()
        gesture_label.setText("\nGestures")
        self.__layout.addWidget(gesture_label)

        self.__gesture_list = QtWidgets.QListWidget()
        self.__gesture_list.itemSelectionChanged.connect(self.__selected_gesture_changed)
        self.__layout.addWidget(self.__gesture_list)

    def __selected_gesture_changed(self):
        self.__handle_stop_training()

        if self.__gesture_model.is_gestures_empty():
            return

        self.__gesture_model.set_selected_gesture_name(self.__gesture_list.currentItem().text())

    def __connect_signals(self):
        self.__gesture_model.gesture_name_exists.connect(self.__show_gesture_name_exists)
        self.__gesture_model.pre_gestures_added.connect(self.__handle_gestures_added)
        self.__gesture_model.gesture_item_added.connect(self.__add_gesture_item)
        self.__gesture_model.state_changed.connect(self.__handle_state_changed)

    def __handle_gestures_added(self, gesture_names):
        for name in gesture_names:
            self.__add_gesture_item(name)

    def __add_gesture_item(self, gesture_name: str):
        gesture_item = QtWidgets.QListWidgetItem(gesture_name)
        self.__gesture_list.addItem(gesture_item)
        self.__gesture_list.setCurrentItem(gesture_item)

    def __show_gesture_name_exists(self, gesture_name: str):
        QtWidgets.QMessageBox.warning(self, "Gesture exists",
                                      "Gesture \"{}\" already exists. (-_-)".format(gesture_name))

    def __show_gesture_accept_removal(self):
        gesture_name = self.__gesture_list.currentItem().text()

        remove_reply = QtWidgets.QMessageBox.question(self, "Remove gesture", "Are you sure to remove gesture \"{}\".\n"
                                                                              "This action can't be undone."
                                                      .format(gesture_name))

        if remove_reply == QtWidgets.QMessageBox.Yes:
            self.__gesture_model.remove_gesture(gesture_name)
            self.__gesture_list.takeItem(self.__gesture_list.currentRow())

    def __show_gesture_accept_retrain(self):
        gesture_name = self.__gesture_list.currentItem().text()

        retrain_reply = QtWidgets.QMessageBox.question(self, "Retrain gesture",
                                                       "Are you sure to retrain gesture \"{}\".\n"
                                                       "All trained data of this gesture will be removed.\n"
                                                       "This action can't be undone."
                                                       .format(gesture_name))

        if retrain_reply == QtWidgets.QMessageBox.Yes:
            self.__gesture_model.retrain_gesture(gesture_name)
            self.__select_training_button_clicked()

    def get_gesture_model(self):
        return self.__gesture_model


class GestureNodeModel(QObject):
    GESTURE_NAME = "gesture_name"
    GESTURE_DATA = "gesture_data"
    GESTURE_ID = "id"

    state_changed = pyqtSignal([GestureNodeState])
    gesture_name_exists = pyqtSignal([str])
    gesture_item_added = pyqtSignal([str])
    pre_gestures_added = pyqtSignal([list])

    def __init__(self):
        super().__init__()

        self.__gestures = []
        self.__id_count = 0
        self.__gesture_state = GestureNodeState.INACTIVE
        self.__is_training = False
        self.__selected_gesture_name = None
        self.__classifier = svm.SVC(kernel="linear")

    def __exists_gesture_name(self, gesture_name: str):
        for gesture in self.__gestures:
            if gesture[self.GESTURE_NAME] == gesture_name:
                return True

        return False

    def __find_gesture_by_name(self, gesture_name):
        return next((gesture for gesture in self.__gestures if gesture[self.GESTURE_NAME] == gesture_name), None)

    def __notify_pre_added_gestures(self):
        gesture_names = []
        for gesture in self.__gestures:
            gesture_names.append(gesture[self.GESTURE_NAME])

        self.pre_gestures_added.emit(gesture_names)

    def setup_pre_added_gestures(self):
        self.__add_gesture_name_to_gestures("stand")
        self.__add_gesture_name_to_gestures("hop")
        self.__add_gesture_name_to_gestures("shake")

        self.__notify_pre_added_gestures()

    def __add_gesture_name_to_gestures(self, gesture_name):
        self.__gestures.append({self.GESTURE_ID: self.__id_count,
                                self.GESTURE_NAME: gesture_name,
                                self.GESTURE_DATA: []})
        self.__id_count += 1

    def add_gesture(self, gesture_name: str):
        if self.__exists_gesture_name(gesture_name):
            self.gesture_name_exists.emit(gesture_name)
            return

        self.__add_gesture_name_to_gestures(gesture_name)

        self.gesture_item_added.emit(gesture_name)

    def remove_gesture(self, gesture_name: str):
        self.__gestures = [gesture for gesture in self.__gestures if not (gesture[self.GESTURE_NAME] == gesture_name)]

        if self.is_gestures_empty():
            self.__selected_gesture_name = None

        self.train_gestures()  # all gestures have to be trained again

    def is_gestures_empty(self):
        return not self.__gestures

    def get_gesture_state(self):
        return self.__gesture_state

    def set_gesture_state(self, state):
        self.__gesture_state = state
        self.state_changed.emit(state)

    def set_selected_gesture_name(self, gesture_name):
        self.__selected_gesture_name = gesture_name

    def is_training(self):
        return self.__is_training

    def set_is_training(self, is_training):
        self.__is_training = is_training

    def collect_training_data(self, gesture_input):
        if not self.__is_training:
            return

        selected_gesture = self.__find_gesture_by_name(self.__selected_gesture_name)
        selected_gesture[self.GESTURE_DATA].append(gesture_input[NodeKey.GESTURE_DATA.value])

    def retrain_gesture(self, gesture_name: str):
        gesture = self.__find_gesture_by_name(gesture_name)
        gesture[self.GESTURE_DATA] = []  # clear gesture data
        self.train_gestures()  # all gestures have to be trained again

    def train_gestures(self):
        # adjusted to our needs -> train(self)
        # https://github.com/ITT-21SS-UR/assignment-8-jl-8/blob/main/activity_recognizer.py
        samples = []
        categories = []

        for gesture in self.__gestures:
            gesture_id = gesture[self.GESTURE_ID]

            for data in gesture[self.GESTURE_DATA]:
                samples.append(data[0])
                categories.append(gesture_id)

        if not all(p == categories[0] for p in categories):
            self.__classifier.fit(samples, categories)

        self.set_is_training(False)

    def predict_gesture(self, gesture_input):
        # adjusted to our needs ->  predict(self, kwargs)
        # https://github.com/ITT-21SS-UR/assignment-8-jl-8/blob/main/activity_recognizer.py
        try:
            gesture_data = gesture_input[NodeKey.GESTURE_DATA.value]
            prediction = self.__classifier.predict(gesture_data)
        except NotFittedError:
            return "error while predicting"

        # return the name of the predicted gesture
        for gesture in self.__gestures:
            if gesture[self.GESTURE_ID] == prediction[0]:
                return gesture[self.GESTURE_NAME]

        return "no gesture detected"
