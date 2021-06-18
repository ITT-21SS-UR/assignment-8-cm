from enum import Enum
class NodeType(Enum):
    DIPPID = "DIPPID"
    BUFFER = "Buffer"
    FEATURE_EXTRACTION_FILTER = "FeatureExtractionFilter"
    GESTURE = "Gesture"
    DISPLAY_TEXT = "DisplayText"


class NodeInputOutputType(Enum):  # TODO
    DATA_IN = "dataIn"
    DATA_OUT = "dataOut"
    ACCEL_X = "accelX"
    ACCEL_Y = "accelY"
    ACCEL_Z = "accelZ"
    FREQUENCY_SPECTROGRAM = "frequency"
    SAMPLE = "sample"
    PREDICTED_CATEGORY = "category"
