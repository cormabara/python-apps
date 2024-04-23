from collections import deque

class MyPlotter:

    class Subplot:

        def __init__(self,pos_,subplot_,deep_,title_, label1_,label2_=None,label3_=None,label4_=None):
            self.subplot = subplot_
            self.subplot.title.set_text(title_)
            self.init_val = [0 for i in range(0,deep_)]
            self.vector_index = deque([i for i in range(0,deep_)], maxlen=deep_)

            self.line_1 = None
            self.line_2 = None
            self.line_3 = None
            self.line_4 = None
            self.pos = pos_

            if label1_:
                self.line_1, = self.subplot.plot(self.vector_index, self.init_val, label=label1_, color="red")
            if label2_:
                self.line_2, = self.subplot.plot(self.vector_index, self.init_val, label=label2_, color="blue")
            if label3_:
                self.line_3, = self.subplot.plot(self.vector_index, self.init_val, label=label3_, color="green")
            if label4_:
                self.line_4, = self.subplot.plot(self.vector_index, self.init_val, label=label4_, color="yellow")

            self.subplot.legend()

        def set_y_range(self,min_,max_):
            self.subplot.set_ylim(min_, max_)

        def add_samples(self, queue1_, queue2_, queue3_, queue4_):
            if self.line_1:
                self.line_1.set_ydata(queue1_)
            if self.line_2:
                self.line_2.set_ydata(queue2_)
            if self.line_3:
                self.line_3.set_ydata(queue3_)
            if self.line_4:
                self.line_4.set_ydata(queue4_)

    def __init__(self,plt_,deep_):
        self.plt = plt_
        self.deep = deep_
        self.subplots = list()
        self.figure = self.plt.figure()

    def add_subplot(self,pos_,title_, label1_,label2_=None,label3_=None,label4_=None) -> Subplot:
        subplot = self.figure.add_subplot(pos_)
        lsp = self.Subplot(pos_, subplot, self.deep,  title_, label1_, label2_, label3_, label4_)

        self.subplots.append(lsp)
        self.plt.grid()
        self.plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=0.1)
        return lsp

    def add_samples(self, pos_, queue1_, queue2_=None, queue3_=None, queue4_=None):
        res = list(filter(lambda x: x.pos == pos_, self.subplots))
        if len(res) == 1:
            res[0].add_samples(queue1_, queue2_, queue3_, queue4_)

    def refresh(self):
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()

    def set_subplot_range(self, pos_,  min_, max_):
        res = list(filter(lambda x: x.pos == pos_, self.subplots))
        if len(res) == 1:
            res[0].set_y_range(min_*11/10,max_*11/10)
