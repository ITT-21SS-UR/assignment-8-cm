from enum import Enum

import pyqtgraph.flowchart.library as fclib
from pyqtgraph.flowchart import Node


class NodeType(Enum):
    DIPPID = "DIPPID"
    BUFFER = "Buffer"
    FEATURE_EXTRACTION_FILTER = "FeatureExtractionFilter"
    ACTIVITY_RECOGNITION = "ActivityRecognition"
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


class FeatureExtractionFilterNode(Node):  # FftNode
    nodeName = NodeType.FEATURE_EXTRACTION_FILTER.value

    def __init__(self, name):
        terminals = {
            NodeInputOutputType.ACCEL_X.value: dict(io="in"),
            NodeInputOutputType.ACCEL_Y.value: dict(io="in"),
            NodeInputOutputType.ACCEL_Z.value: dict(io="in"),
            NodeInputOutputType.FREQUENCY_SPECTROGRAM.value: dict(io="out")
        }

        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwargs):
        # TODO
        pass


fclib.registerNodeType(FeatureExtractionFilterNode, [(NodeType.FEATURE_EXTRACTION_FILTER.value,)])


class ActivityRecognitionNode(Node):  # SvmNode
    nodeName = NodeType.ACTIVITY_RECOGNITION.value

    def __init__(self, name):
        terminals = {
            # TODO
            NodeInputOutputType.SAMPLE.value: dict(io="in"),
            NodeInputOutputType.PREDICTED_CATEGORY.value: dict(io="out")
        }

        # TODO UI

        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwargs):
        # TODO
        pass


fclib.registerNodeType(ActivityRecognitionNode, [(NodeType.ACTIVITY_RECOGNITION.value,)])


class DisplayTextNode(Node):
    nodeName = NodeType.DISPLAY_TEXT.value

    def __init__(self, name):
        terminals = {
            # TODO
            NodeInputOutputType.SAMPLE.value: dict(io="in"),
            NodeInputOutputType.PREDICTED_CATEGORY.value: dict(io="out")
        }

        # TODO UI

        Node.__init__(self, name, terminals=terminals)

    def process(self, **kwargs):
        # TODO
        pass


fclib.registerNodeType(DisplayTextNode, [(NodeType.DISPLAY_TEXT.value,)])
