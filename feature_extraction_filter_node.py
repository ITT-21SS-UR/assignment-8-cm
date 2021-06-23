import numpy as np
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.flowchart import Node

from node_constants import NodeKey

"""
A FeatureExtractionFilterNode that reads in the accelerometer values from the BufferNode.
And outputs the average fft over all values and the ffts for each value in a array.
"""


# Author: Claudia
# Reviewer: Martina
class FeatureExtractionFilterNode(Node):
    nodeName = "FeatureExtractionFilter"

    @staticmethod
    def get_node_name():
        return FeatureExtractionFilterNode.nodeName

    def __init__(self, name):
        terminals = {
            NodeKey.ACCEL_X.value: dict(io="in"),
            NodeKey.ACCEL_Y.value: dict(io="in"),
            NodeKey.ACCEL_Z.value: dict(io="in"),

            NodeKey.SPECTROGRAM_AVG.value: dict(io="out"),
            NodeKey.FFT.value: dict(io="out")
        }

        Node.__init__(self, name, terminals=terminals)

    @staticmethod
    def __calculate_frequency(values):
        return np.abs(np.fft.fft(values) / len(values))[1:len(values) // 2]

    def process(self, **kwargs):
        # buffer_size currently has a max size of 32
        # to get more values the buffer_size of BufferNode can be increased

        x = kwargs[NodeKey.ACCEL_X.value]
        y = kwargs[NodeKey.ACCEL_Y.value]
        z = kwargs[NodeKey.ACCEL_Z.value]

        # calculate average fft
        avg = []
        for i in range(len(x)):
            avg.append((x[i]) + y[i] + z[i] / 3)

        fft_avg = FeatureExtractionFilterNode.__calculate_frequency(avg)

        # calculate single ffts and combine them
        fft_x = FeatureExtractionFilterNode.__calculate_frequency(x)
        fft_y = FeatureExtractionFilterNode.__calculate_frequency(y)
        fft_z = FeatureExtractionFilterNode.__calculate_frequency(z)
        fft = np.array([fft_x, fft_y, fft_z])

        return {NodeKey.SPECTROGRAM_AVG.value: fft_avg,  # used to plot the graph
                NodeKey.FFT.value: fft}  # to take all ffts into consideration


fclib.registerNodeType(FeatureExtractionFilterNode, [(FeatureExtractionFilterNode.get_node_name(),)])
