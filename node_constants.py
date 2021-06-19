from enum import Enum


class NodeInputOutputType(Enum):  # TODO
    DATA_IN = "dataIn"
    DATA_OUT = "dataOut"
    ACCEL_X = "accelX"
    ACCEL_Y = "accelY"
    ACCEL_Z = "accelZ"
    FREQUENCY_SPECTROGRAM = "spectrogram"
    SAMPLE = "sample"
    PREDICTED_CATEGORY = "category"
