import numpy as np
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.flowchart import Node

from node_constants import NodeKey


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
            NodeKey.SPECTROGRAM_X.value: dict(io="out"),
            NodeKey.FFT.value: dict(io="out")
        }

        Node.__init__(self, name, terminals=terminals)

    @staticmethod
    def __calculate_frequency(values):
        return np.abs(np.fft.fft(values) / len(values))[1:len(values) // 2]

    def process(self, **kwargs):
        x = kwargs[NodeKey.ACCEL_X.value]
        y = kwargs[NodeKey.ACCEL_Y.value]
        z = kwargs[NodeKey.ACCEL_Z.value]

        avg = []

        # TODO maybe save values from previous processes for getting more data because 14 is a little bit
        #  or increase buffer size

        for i in range(len(x)):
            avg.append((x[i]) + y[i] + z[i] / 3)

        # one accel array of buffer has a max size of 32
        fft_x = self.__calculate_frequency(x)
        fft_y = self.__calculate_frequency(y)
        fft_z = self.__calculate_frequency(z)
        fft = ([fft_x, fft_y, fft_z])  # np.array([fft_x, fft_y, fft_z])

        fft_avg = self.__calculate_frequency(avg)

        # fft2 = np.abs(np.fft.fft(np.hamming(len(avg)) * avg) / len(avg))[1:len(avg) // 2]

        return {NodeKey.SPECTROGRAM_AVG.value: fft_avg,
                NodeKey.SPECTROGRAM_X.value: fft_x,
                NodeKey.FFT.value: fft}  # TODO which fft?


fclib.registerNodeType(FeatureExtractionFilterNode, [(FeatureExtractionFilterNode.get_node_name(),)])
