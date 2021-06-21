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
    #  Y = Y[0:int(n/2)] # use only first half as the function is mirrored  # das hier braucht man stf
    #
    #  plot(frq, abs(Y),'r') # plotting the spectrum  # und das hier laut stf
    #  xlabel('Frequency (Hz)')
    #  ylabel('Intensity')

    def process(self, **kwargs):
        fft_x = np.fft.fft(kwargs[NodeKey.ACCEL_X.value])
        fft_y = np.fft.fft(kwargs[NodeKey.ACCEL_Y.value])
        fft_z = np.fft.fft(kwargs[NodeKey.ACCEL_Z.value])
        fft = np.array(np.array((fft_x, fft_y, fft_z)))

        # TODO only for testing
        time_signal = np.array(kwargs[NodeKey.ACCEL_Y.value][0])

        # TODO output gesture node
        return {NodeKey.TIME_SIGNAL_X.value: time_signal,
                NodeKey.SPECTROGRAM_X.value: np.array(kwargs[NodeKey.ACCEL_Y.value]),
                NodeKey.FFT.value: fft}


fclib.registerNodeType(FeatureExtractionFilterNode, [(FeatureExtractionFilterNode.get_node_name(),)])
