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

            NodeKey.TIME_SIGNAL_X.value: dict(io="out"),  # TODO only for testing?
            NodeKey.SPECTROGRAM_X.value: dict(io="out"),
            NodeKey.FFT.value: dict(io="out")
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
    #  T = n / Fs  (Fs ist 20 in DIPPID conn stehts drin)
    #  frq = k / T # two sides frequency range
    #  frq = frq[0:int(n/2)] # one side frequency range
    #
    #
    #  Y = fft.fft(y) / n # fft computing and normalization
    #  Y = Y[0:int(n/2)] # use only first half as the function is mirrored  # das hier braucht man?
    #
    #  plot(frq, abs(Y),'r') # plotting the spectrum  # und das hier?
    #  xlabel('Frequency (Hz)')
    #  ylabel('Intensity')

    def __calculate_frequency(self, values):
        return [np.abs(np.fft.fft(values) / len(values))[1:len(values) // 2]]

    def process(self, **kwargs):
        # FFT, stddev, derivatives
        # one accel array of buffer has a max size of 32
        fft_x = self.__calculate_frequency(kwargs[NodeKey.ACCEL_X.value])
        fft_y = self.__calculate_frequency(kwargs[NodeKey.ACCEL_Y.value])
        fft_z = self.__calculate_frequency(kwargs[NodeKey.ACCEL_Z.value])
        fft = np.array([fft_x, fft_y, fft_z])

        return {NodeKey.TIME_SIGNAL_X.value: np.array(kwargs[NodeKey.ACCEL_X.value]),  # time signal x
                NodeKey.SPECTROGRAM_X.value: fft_x,  # spectrogram x
                NodeKey.FFT.value: fft}


fclib.registerNodeType(FeatureExtractionFilterNode, [(FeatureExtractionFilterNode.get_node_name(),)])
