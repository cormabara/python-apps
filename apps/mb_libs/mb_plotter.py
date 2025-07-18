from collections import deque

import matplotlib
import numpy as np

from mb_types import dm_sign


class MbPlotter:

    class MidPlot:
        colors_single = [ "r","b","g","y","c","tab:purple","gray","m","tab:pink","tab:orange"]
        # colors_gradiation = plt.cm.get_cmap("viridis")(np.linspace(0, 1, 10))
        colors_gradiation = matplotlib.colormaps["viridis"](np.linspace(0, 1, 10))
        def __init__(self,pos_,subplot_,deep_,title_):
            self.subplot = subplot_
            self.subplot.title.set_text(title_)
            self.init_val = [0 for i in range(0,deep_)]
            self.vector_index = deque([i for i in range(0,deep_)], maxlen=deep_)

            self.line_v = list()
            self.pos = pos_
            self.colors = self.colors_single

        def set_gradiation(self):
            self.colors = self.colors_gradiation

        def set_colors(self):
            self.colors = self.colors_single

        def set_labels(self,labelv_):
            for ii in range(0,len(labelv_)):
                tmp, = self.subplot.plot(self.vector_index, self.init_val, label=labelv_[ii], color=self.colors[ii])
                self.line_v.append(tmp)

            self.subplot.legend()

        def add_samples(self, datav_):
            max_v = list()
            min_v = list()
            if len(datav_):
                for ii in range(0, len(datav_)):
                    if not datav_[ii] is None and self.line_v[ii]:
                        self.line_v[ii].set_ydata(datav_[ii])
                        max_v.append(max(datav_[ii]))
                        min_v.append(min(datav_[ii]))

                min_final = min(min_v)
                max_final = max(max_v)
            else:
                max_final = 0
                min_final = 0

            if max_final > 0:
                max_final *= 11 / 10
            elif max_final == 0:
                max_final += -min_final/10
            else:
                max_final *= 9 / 10

            if min_final > 0:
                min_final *= 9 / 10
            elif min_final == 0:
                min_final += -max_final / 10
            else:
                max_final *= 11 / 10

            self.subplot.set_ylim(min_final, max_final)

        def set_y_range(self,min_,max_):
            self.subplot.set_ylim(min_, max_)

    def __init__(self,plt_,deep_):
        self.plt = plt_
        self.deep = deep_
        self.subplots = list()
        self.figure = self.plt.figure()

    def add_subplot(self, pos_, title_, labelv_,gradient_=False) -> MidPlot:
        subplot = self.figure.add_subplot(pos_)
        lsp = self.MidPlot(pos_, subplot, self.deep, title_)
        if gradient_:
            lsp.set_gradiation()
        lsp.set_labels(labelv_)
        self.subplots.append(lsp)
        self.plt.grid()
        self.plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.1)
        return lsp

    def add_samples(self, pos_, queue_v):
        res = list(filter(lambda x: x.pos == pos_, self.subplots))
        if len(res) == 1 and len(queue_v):
            res[0].add_samples(queue_v)

    def add_channel(self, pos_, title_, labelv_, queuev_, gradient_=False):
        ch = self.add_subplot(pos_, title_, labelv_,gradient_)
        ch.set_gradiation()
        self.add_samples(pos_, queuev_)

    def refresh(self):
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def set_subplot_range(self, pos_,  min_, max_):
        res = list(filter(lambda x: x.pos == pos_, self.subplots))
        if len(res) == 1:
            res[0].set_y_range(min_*11/10,max_*11/10)

