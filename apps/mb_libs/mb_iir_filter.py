# Class for a IIR filter definition with the same algorithm used inside DICE

import math

import numpy as np

from config import WorkMode
from mb_trigo import pix2e16
from mb_types import U32_MAX, set_s32


class LPF32_IIR_Filter:

    CIF_LPF_IIR_SHIFTSTRAND = 18

    def __init__(self,mode_, freq_cut_mHz_, freq_sample_Hz_):
        ''' Constructor of the filter with sample frequency and cut frequeny
        If cut frequency is 0 the filter is disabled '''
        self._Wt = 0
        self._xt8 = 0
        self._wt18 = 0
        self.mode = mode_
        self._xt18 = np.int64(0)
        self._xt16 = np.int64(0)
        self.SetWt(set_s32(freq_cut_mHz_), set_s32(freq_sample_Hz_))
        self._accumulator = np.int64(0)

    def SetWt(self, Fcut_mHz_, Fsam_Hz_):

        self._Fsample_Hz = Fsam_Hz_
        self._Fcut_mHz = Fcut_mHz_

        # se la frequenza di taglio permette l'utilizzo della massima risoluzione...
        if Fcut_mHz_ < (U32_MAX / (pix2e16 / 125)):
            self._xt18 = (pix2e16 / 125) * self._Fcut_mHz
            self._wt18 = self._xt18 / (self._Fsample_Hz + (self._xt18 / 2 ** self.CIF_LPF_IIR_SHIFTSTRAND))
            self._xt8 = self._xt18 / 2 ** 10
        else:
            self._xt16 = (pix2e16 / 125) * (self._Fcut_mHz / 2 ** 2)
            self._wt18 = self._xt16 / ((self._Fsample_Hz + (self._xt16 / 2 ** 16)) / 2 ** 2)
            self._xt8 = self._xt16 / 2 ** 8

        # se il calcolo del parametro ritorna 0 ma la frequenza di taglio e' != 0 => satura parametri a 1
        if Fcut_mHz_:
            if self._wt18 < 1:
                self._wt18 = 1
            if self._xt8 < 1:
                self._xt8 = 1

        self._Wt = self._wt18

    # Reset the accumulator of the filter
    def reset(self):
        self._accumulator = 0

    def preset(self, sample_: float):
        self._accumulator = sample_ * (2 ** self.CIF_LPF_IIR_SHIFTSTRAND)

    # calcolo filtro passabasso (la chiamata va fatta alla frequenza di campionamento definita nella init)
    def filter(self, sample_):

        if self.mode == WorkMode.dice:
            sample_ = set_s32(sample_)
            if self._Fcut_mHz:
                err = set_s32(sample_ - (self._accumulator / (2 ** self.CIF_LPF_IIR_SHIFTSTRAND)))
                self._accumulator += set_s32(err * self._Wt)
                sample_ = set_s32(self._accumulator / (2 ** self.CIF_LPF_IIR_SHIFTSTRAND))
                return set_s32(sample_)
        else:
            if self._Fcut_mHz:
                err = sample_ - (self._accumulator / (2 ** self.CIF_LPF_IIR_SHIFTSTRAND))
                self._accumulator += err * self._Wt
                sample_ = self._accumulator / (2 ** self.CIF_LPF_IIR_SHIFTSTRAND)
                return sample_

    # Get the value of the filter
    def get_val(self):
        if self.mode == WorkMode.dice:
            return set_s32(self._accumulator/(2 ** self.CIF_LPF_IIR_SHIFTSTRAND))
        else:
            return self._accumulator/(2 ** self.CIF_LPF_IIR_SHIFTSTRAND)

