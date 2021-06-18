import pyqtgraph.flowchart.library as fclib
from pyqtgraph.flowchart import Node

from node_constants import NodeType, NodeInputOutputType


class FeatureExtractionFilterNode(Node):
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


class DisplayTextNode(Node):  # TODO move to separate file
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
