""" This file implement the CSV interface """
import locale
from os.path import exists
from tkinter import Tk
from tkinter.filedialog import askopenfilename

import numpy
import numpy as np
from pandas import DataFrame
from scanf import scanf

import pandas

from mb_dialogs import mb_file_chooser
from mb_logger import Logger


def array_to_csv(fn_, index_, data_):
    df = DataFrame()

    locale.setlocale(locale.LC_ALL, 'it_IT.UTF-8')
    fiv = [locale.format_string("%f", np.array(i), grouping=True) for i in index_]
    df.insert(0, str("index"), np.array(fiv))

    # Setting the locale to 'it_IT' (Italian)
    data = np.array(data_)
    fdv = [locale.format_string("%f", np.array(d), grouping=True) for d in data]
    df.insert(1, str("values"), np.array(fdv))

    df.to_csv(path_or_buf=fn_, sep=';', columns=["index","values"], index=True, mode='w', encoding='utf-8')


class MbCsv:

    def __init__(self, filename_=None):
        Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
        self.filename = filename_
        if not self.filename:
            self.filename = mb_file_chooser()  # show an "Open" dialog box and return the path to the selected file

        if not exists(self.filename):
            Logger().error(-1,"Cannot load the " + self.filename + "!")



class MbCsvOscillo(MbCsv):
    MAXNUMCOLS = 8

    class MbOscCh:

        def __init__(self,index_,name_,data_):
            # var01 sw[0x604107]
            self.index = index_
            self.name = name_
            tmp_list = scanf("var%d sw[%s]", str(data_[0]))
            self.data = data_[1:]
            self.data = [int(s) for s in self.data]

            self.num_col = str(tmp_list[0])
            self.mux = str(tmp_list[1])


    def __init__(self, filename_=None):
        MbCsv.__init__(self,filename_)
        self.osc_data = list()

    def load_data_from_csv(self, name_list_):
        Logger().print("\nLoad values from CSV oscilloscope: " + self.filename)

        for my_iter in range(len(name_list_)):
            col = self.MbOscCh(my_iter,name_list_[my_iter],pandas.read_csv(self.filename, usecols=[my_iter], header=19).to_numpy())
            self.osc_data.append(col)

    def get_chn(self,name_) -> MbOscCh|None:
        chn = list(filter(lambda x: x.name == name_, self.osc_data))
        if len(chn) != 1:
            return None
        else:
            return chn[0]

    def get_chn_values(self,channel_,size_):
        chn = list(filter(lambda x: x.name == channel_, self.osc_data))
        if len(chn) != 1:
            return None
        if not size_:
            # if size is 0 take all the samples
            return chn[0].data
        elif len(chn[0].data) < size_:
            return numpy.append(chn[0].data,[0 for i in (0,size_-len(chn[0].data))])
        elif len(chn[0].data) > size_:
            return chn[0].data[0:size_]
        else:
            return chn[0].data

    def save_data_to_csv(self, fn_,channels_):
        """ This function get a vector of channels (of the Tracer) and create a csv file """
        # Controllo che tutte le colonne siano lunghe uguali, else errore
        df = DataFrame()
        for ch_id in channels_:
            ch = self.get_chn(ch_id)
            df.insert(0, str(ch.name), np.array(ch.data))

        df.to_csv(path_or_buf=fn_, sep=',', columns=channels_, index=True, mode='w', encoding='utf-8')
