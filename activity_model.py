from PyQt5.QtCore import QObject


class ActivityModel(QObject):
    # TODO

    def __init__(self, port_number):
        super().__init__()
        self.__port_number = port_number

    def get_port_number(self):
        return self.__port_number
