from enum import Enum


class NodeKey(Enum):
    DATA_IN = "dataIn"
    DATA_OUT = "dataOut"
    ACCEL_X = "accelX"
    ACCEL_Y = "accelY"
    ACCEL_Z = "accelZ"
    TIME_SIGNAL_X = "time_signal_x"  # probably not needed
    SPECTROGRAM_X = "spectrogram_x"
    SPECTROGRAM_Y = "spectrogram_y"
    SPECTROGRAM_Z = "spectrogram_z"
    FFT = "fft"
    DISPLAY_TEXT = "displayText"
    GESTURE_DATA = "data"
    TEXT = "text"
    PREDICTED_GESTURE = "name"
