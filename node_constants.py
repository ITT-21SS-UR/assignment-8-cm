from enum import Enum

"""
Input and Output keys of the node dicts
"""


# Author: Claudia
# Reviewer: Martina
class NodeKey(Enum):
    DATA_IN = "dataIn"
    DATA_OUT = "dataOut"
    ACCEL_X = "accelX"
    ACCEL_Y = "accelY"
    ACCEL_Z = "accelZ"
    SPECTROGRAM_AVG = "fft_avg"
    FFT = "fft"
    DISPLAY_TEXT = "displayText"
    GESTURE_DATA = "gestureIn"
    TEXT = "text"
    PREDICTED_GESTURE = "name"
