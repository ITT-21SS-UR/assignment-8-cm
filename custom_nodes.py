import numpy as np
import pyqtgraph.flowchart.library as fclib
from pyqtgraph.flowchart import Node

from node_constants import NodeInputOutputType


class FeatureExtractionFilterNode(Node):
    nodeName = "FeatureExtractionFilter"

    @staticmethod
    def get_node_name():
        return FeatureExtractionFilterNode.nodeName

    def __init__(self, name):
        terminals = {
            NodeInputOutputType.ACCEL_X.value: dict(io="in"),
            NodeInputOutputType.ACCEL_Y.value: dict(io="in"),
            NodeInputOutputType.ACCEL_Z.value: dict(io="in"),
            NodeInputOutputType.FREQUENCY_SPECTROGRAM.value: dict(io="out")
        }

        Node.__init__(self, name, terminals=terminals)

    # def plotSpectrum(y, Fs):
    #  """
    #  Plots a Single-Sided Amplitude Spectrum of y(t)
    #  http://glowingpython.blogspot.de/2011/08/how-to-plot-frequency-spectrum-with.html
    #
    #  Frequency Spectrum: composition of a Signal's individual frequencies
    #  Amplitude Spectrum: the absolute value of the Frequency Spectrum
    #  """
    #  n = len(y) # length of the signal
    #  k = arange(n)
    #  T = n / Fs
    #  frq = k / T # two sides frequency range
    #  frq = frq[0:int(n/2)] # one side frequency range
    #
    #
    #  Y = fft.fft(y) / n # fft computing and normalization
    #  Y = Y[0:int(n/2)] # use only first half as the function is mirrored
    #
    #  plot(frq, abs(Y),'r') # plotting the spectrum
    #  xlabel('Frequency (Hz)')
    #  ylabel('Intensity')

    def __calculate_frequency(self):
        # TODO calculate frequency
        return 5

    def process(self, **kwargs):
        fft_x = np.fft.fft(kwargs[self.ACCEL_X])
        fft_y = np.fft.fft(kwargs[self.ACCEL_Y])
        fft_z = np.fft.fft(kwargs[self.ACCEL_Z])

        #  normal_x = -kwargs["accelX"][0]
        #         normal_y = kwargs["accelZ"][0]
        #
        #         self.__rotation_vectors = np.array(((0, 0), (normal_x, normal_y)))
        #
        #         return {"rotation": self.__rotation_vectors}

        print("s")

        # x should be the calculated frequency and y the amplitude or intensity?
        return {NodeInputOutputType.FREQUENCY_SPECTROGRAM.value: np.array([fft_x, fft_y, fft_z])}


fclib.registerNodeType(FeatureExtractionFilterNode, [(FeatureExtractionFilterNode.get_node_name(),)])


class DisplayTextNode(Node):  # TODO move to separate file
    nodeName = "DisplayText"

    @staticmethod
    def get_node_name():
        return DisplayTextNode.nodeName

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


fclib.registerNodeType(DisplayTextNode, [(DisplayTextNode.get_node_name(),)])
