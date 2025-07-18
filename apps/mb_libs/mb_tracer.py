from collections import deque

import numpy as np
from matplotlib import pyplot as plt
from pandas import DataFrame

from config import MbConfig
from mb_logger import Logger
from mb_plotter import MbPlotter
from mb_tools import SingletonMeta

from scipy.fft import fft, fftfreq
import numpy as np
import matplotlib.pyplot as plt


class Tracer(metaclass=SingletonMeta):
    class DbgTraceCh:
        """ Definition of a single channel for debug tracing """

        def __init__(self, id_):
            self.id = id_
            self._samples = deque([0 for i in range(0, MbConfig().win_deep)], maxlen=MbConfig().win_deep)

        def append(self, sample_):
            self._samples.append(sample_)

        def samples(self):
            return self._samples

    def __init__(self):
        self.debugChannels = list()
        self.dummy = deque([0 for i in range(0, MbConfig().win_deep)], maxlen=MbConfig().win_deep)

    def ch_get(self, ch_) -> DbgTraceCh | None:
        """ Find a channel by ch_ s the id of the channel """
        channels = list(filter(lambda x: x.id == ch_, self.debugChannels))
        if len(channels) > 0:
            return channels[0]
        return None

    def ch_clear(self, ch_):
        channels = list(filter(lambda x: x.id == ch_, self.debugChannels))
        if len(channels) > 0:
            channels[0].clear()

    def ch_add(self, ch_) -> DbgTraceCh:
        """ Add a new channel with id = ch_ """
        channels = list(filter(lambda x: x.id == ch_, self.debugChannels))
        numch = len(channels)
        if numch == 0:
            channel = self.DbgTraceCh(ch_)
            self.debugChannels.append(channel)
        elif numch > 1:
            Logger().warning("More than one channel inside the trace with same id: " + str(ch_))
            channel = channels[0]
            channel.clear()
        else:
            channel = channels[0]
            channel.clear()
        return channel

    def ch_remove(self, ch_):
        res = list(filter(lambda x: x.id == ch_, self.debugChannels))
        if len(res) == 1:
            self.debugChannels.remove(res)

    def ch_samples(self, ch_):
        ch = self.ch_get(ch_)
        if ch:
            return ch.samples()
        else:
            return self.dummy

    def ch_samples_v(self, ch_):
        ch = self.ch_get(ch_)
        if ch:
            return np.array(ch.samples())
        else:
            return np.array(self.dummy)

    def add_sample(self, ch_, sample_):
        res = list(filter(lambda x: x.id == ch_, self.debugChannels))
        if len(res) == 0:
            channel = self.ch_add(ch_)
        else:
            channel = res[0]

        channel.append(sample_)

    def add_sample_v(self, ch_, samples_):
        res = list(filter(lambda x: x.id == ch_, self.debugChannels))
        if len(res) == 0:
            channel = self.ch_add(ch_)
        else:
            channel = res[0]

        channel.append(samples_)

    def set_plot(self, title_, ch_v_):
        pid_cdyn = MbPlotter(plt, MbConfig().win_deep)
        pos_fig = 111
        labels = [self.ch_get(i).id for i in ch_v_]
        data = [self.ch_get(i).samples() for i in ch_v_]
        pid_cdyn.add_subplot(pos_fig, title_, labels)
        pid_cdyn.add_samples(pos_fig, data)
        return pid_cdyn

    def plot(self, plt_, title_, deep_, channels_):
        graph = MbPlotter(plt_, deep_)
        pos_fig = 111
        graph.add_subplot(pos_fig, title_, [self.ch_get(i).id for i in channels_])
        graph.add_samples(pos_fig, [self.ch_get(i).samples() for i in channels_])

    def to_csv(self,fn_,title_, deep_, channels_):
        """ This function get a vector of channels (of the Tracer) and create a csv file """
        # Controllo che tutte le colonne siano lunghe uguali, else errore
        df = DataFrame()
        for ch_id in channels_:
            ch = self.ch_get(ch_id)
            df.insert(0,str(ch.id),np.array(ch.samples()))

        df.to_csv(path_or_buf=fn_, sep=',', columns=channels_, index=True, mode='w', encoding='utf-8')

    def to_fourier(self,fn_,ch_):
        ch = self.ch_get(ch_)
        samples = len(ch.samples())
        spacing = 1/10000
        # Compute the FFT
        yf = fft(ch.samples())
        xf = fftfreq(samples, spacing)[:samples // 2]

        # Plot the results
        plt.plot(xf, 2.0 / samples * np.abs(yf[0:samples // 2]))
        plt.grid()
        plt.show()
