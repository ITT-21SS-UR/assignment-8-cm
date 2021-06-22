from enum import Enum


class NodeKey(Enum):
    DATA_IN = "dataIn"
    DATA_OUT = "dataOut"
    ACCEL_X = "accelX"
    ACCEL_Y = "accelY"
    ACCEL_Z = "accelZ"
    SPECTROGRAM_AVG = "spectrogram_avg"
    SPECTROGRAM_X = "spectrogram_x"
    FFT = "fft"
    DISPLAY_TEXT = "displayText"
    GESTURE_DATA = "data"
    TEXT = "text"
    PREDICTED_GESTURE = "name"
