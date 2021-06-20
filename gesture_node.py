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
            NodeKey.GESTURE_DATA.value: dict(io="in"),
            NodeKey.PREDICTED_GESTURE.value: dict(io="out")
        }

        self.__gesture_node_widget = GestureNodeWidget()

        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwargs):
        gesture_model = self.__gesture_node_widget.get_gesture_model()
        gesture_state = gesture_model.get_gesture_state()

        if gesture_state == GestureNodeState.TRAINING:
            gesture_model.train_gesture(kwargs)
        elif gesture_state == GestureNodeState.PREDICTION:
            gesture_model.predict_gesture(kwargs)

    def ctrlWidget(self):
        return self.__gesture_node_widget


fclib.registerNodeType(GestureNode, [(GestureNode.nodeName,)])


class GestureNodeWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        self.__gesture_model = GestureNodeModel()
        self.__setup_layout()

    def __setup_layout(self):
        self.__layout = QtWidgets.QVBoxLayout()

        self.__setup_gesture_state_selection_layout()
        self.__setup_gesture_button_layout()
        self.__setup_info_text()
        self.__setup_training_button()
        self.__setup_gesture_list()

        self.__handle_state_changed(self.__gesture_model.get_gesture_state())
        self.__connect_signals()

        self.setLayout(self.__layout)

    def __setup_gesture_state_selection_layout(self):
        self.__state_selection_layout = QtWidgets.QVBoxLayout()

        self.__setup_select_training_button()
        self.__setup_prediction_button()
        self.__setup_inactive_button()

        self.__layout.addLayout(self.__state_selection_layout)

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
        # TODO stop current training when is being trained
        if state == GestureNodeState.TRAINING:
            self.__info_text.setText("To train your gesture click \"Begin Training\".\n"
                                     "Click on \"Training...\" to stop the training.")
            self.__training_button.show()
        elif state == GestureNodeState.PREDICTION:
            # TODO check how many trained gestures are available and change text accordingly
            self.__info_text.setText("Predicted gesture is shown in DisplayText.")
            self.__training_button.hide()
        elif state == GestureNodeState.INACTIVE:
            self.__info_text.setText("Select another state to train or predict a gesture.")
            self.__training_button.hide()

    def __setup_training_button(self):
        self.__training_button = QtWidgets.QPushButton()
        self.__training_button.setText("Begin Training")
        self.__training_button.clicked.connect(self.__training_button_clicked)
        self.__layout.addWidget(self.__training_button)

    def __training_button_clicked(self):
        if self.__gesture_model.is_training():
            self.__training_button.setText("Begin Training")
            self.__gesture_model.stop_training()
        else:
            self.__training_button.setText("Training...")
            self.__gesture_model.collect_training_data()

        self.__gesture_model.reverse_is_training()

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
        QtWidgets.QMessageBox.warning(self, "No gesture selected", "No gesture was selected.\n"
                                                                   "Please select or add a gesture.")

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
        self.__gesture_model.state_changed.connect(self.__handle_state_changed)

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
            self.__select_training_button_clicked()

    def get_gesture_model(self):
        return self.__gesture_model


class GestureNodeModel(QObject):
    GESTURE_NAME = "gesture_name"
    GESTURE_DATA = "gesture_data"

    state_changed = pyqtSignal([GestureNodeState])
    gesture_name_exists = pyqtSignal([str])
    gesture_item_added = pyqtSignal([str])

    def __init__(self):
        super().__init__()
        self.__gestures = []
        self.__classifier = svm.SVC()  # TODO which type?
        self.__setup_pretrained_gestures()
        self.__gesture_state = GestureNodeState.INACTIVE
        self.__is_training = False

    @staticmethod
    def __read_data(file_name):
        # Wiimote - FFT - SVM.ipynb
        # TODO in practice, you would do this with csv.Reader or pandas
        x = []
        y = []
        z = []
        avg = []

        for line in open(file_name, "r").readlines():
            _x, _y, _z = map(int, line.strip().split(","))
            x.append(_x)
            y.append(_y)
            z.append(_z)
            avg.append((_x + _y + _z) / 3)

        return avg

    def __setup_pretrained_gestures(self):
        # source slightly modified: Wiimote - FFT - SVM.ipynb
        # TODO setup pretrained gestures: use csv hop stand walk from data folder
        stand_csv = ["./data/stand_1.csv", "./data/stand_2.csv", "./data/stand_3.csv", "./data/stand_4.csv"]
        walk_csv = ["./data/walk_1.csv", "./data/walk_2.csv", "./data/walk_3.csv", "./data/walk_4.csv"]
        hop_csv = ["./data/hop1.csv", "./data/hop2.csv", "./data/hop3.csv", "./data/hop4.csv"]

        stand_raw = [GestureNodeModel.__read_data(f) for f in stand_csv]
        walk_raw = [GestureNodeModel.__read_data(f) for f in walk_csv]
        hop_raw = [GestureNodeModel.__read_data(f) for f in hop_csv]

        # print(stand_raw)

        # samples = list(zip(x, y, z)) # for each csv column map them to a tuple with (x,y,z)
        # self.__gestures = # TODO set pretrained gestures

    def __exists_gesture_name(self, gesture_name: str):
        for gesture in self.__gestures:
            if gesture[self.GESTURE_NAME] == gesture_name:
                return True

        return False

    def __find_gesture_by_name(self, gesture_name):
        return next((gesture for gesture in self.__gestures if gesture[self.GESTURE_NAME] == gesture_name), None)

    def add_gesture(self, gesture_name: str):
        if self.__exists_gesture_name(gesture_name):
            self.gesture_name_exists.emit(gesture_name)
            return

        self.__gestures.append({self.GESTURE_NAME: gesture_name,
                                self.GESTURE_DATA: []})

        self.gesture_item_added.emit(gesture_name)

    def predict_gesture(self, gesture_input):
        # TODO predict_gesture
        # label predicted gesture:
        # name of predicted gesture min requirement 1 gesture to start prediction
        # classifier.fit(samples, c1)  # TODO for training
        # u_class = classifier.predict([[xu, yu]])
        # print(u_class)

        pass

    def remove_gesture(self, gesture_name: str):
        self.__gestures = [gesture for gesture in self.__gestures if not (gesture[self.GESTURE_NAME] == gesture_name)]

    def get_gesture_state(self):
        return self.__gesture_state

    def set_gesture_state(self, state):
        self.__gesture_state = state
        self.state_changed.emit(state)

    def train_gesture(self, gesture_input):
        # TODO train gesture
        # TODO get selected item
        if not self.__is_training:
            return

        # selected_gesture = self.__find_gesture_by_name(gesture_name)
        # print(selected_gesture)
        # Add gesture_data to current selected_gesture

        # Push button
        # Begin training
        # Stop training

        pass

    def retrain_gesture(self, gesture_name: str):
        gesture = self.__find_gesture_by_name(gesture_name)
        gesture[self.GESTURE_DATA] = []

    def is_training(self):
        return self.__is_training

    def reverse_is_training(self):
        self.__is_training = not self.__is_training

    def stop_training(self):
        print("stop training")

    def collect_training_data(self):
        print("start training")


class GestureItemData:
    # TODO GestureItemData needed?
    pass
