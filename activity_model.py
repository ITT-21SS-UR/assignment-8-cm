

from PyQt5.QtCore import QObject




class ActivityModel(QObject):
    # TODO

    def __init__(self, port_number):
        super().__init__()
        self.__port_number = port_number

    def add_gesture(self):
        pass

    def train_gesture(self):
        pass

    def predict_gesture(self):
        pass

    def remove_gesture(self):
        pass

    def get_port_number(self):
        return self.__port_number
