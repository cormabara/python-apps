# Class for a IIR filter definition with the same algorithm used inside DICE

import math
from f_dice.lib.types import U32_MAX


class IIRFilter:

    CIF_LPF_IIR_SHIFTSTRAND = 18
    PIX2E16 = 205887

    _Fsample_Hz: float          # Sample frequency of the filter in Hz
    _Fcut_mHz: float             # Cut frequency in Hz
    _accumulator: float          # Accumulator for the filter
    _xt8: float
    _wt18: float
    _wt16: float

    _Wt: float

    def __init__(self, freq_cut_mHz_: float, freq_sample_Hz_: float):
        ''' Constructor of the filter with sample frequency and cut frequeny
        If cut frequency is 0 the filter is disabled '''
        self._xt18: float = 0
        self._xt16: float = 0
        self.SetWt(freq_cut_mHz_, freq_sample_Hz_)
        self._accumulator = 0

    def SetWt(self, Fcut_mHz_, Fsam_Hz_):

        self._Fsample_Hz = Fsam_Hz_
        self._Fcut_mHz = Fcut_mHz_

        # se la frequenza di taglio permette l'utilizzo della massima risoluzione...
        if Fcut_mHz_ < (U32_MAX / (self.PIX2E16 / 125)):
            self._xt18 = (self.PIX2E16 / 125) * self._Fcut_mHz
            self._wt18 = self._xt18 / (self._Fsample_Hz + (self._xt18 / 2 ** self.CIF_LPF_IIR_SHIFTSTRAND))
            self._xt8 = self._xt18 / 2 ** 10
        else:
            self._xt16 = (self.PIX2E16 / 125) * (self._Fcut_mHz / 2 ** 2)
            self._wt18 = self._xt16 / ((self._Fsample_Hz + (self._xt16 / 2 ** 16)) / 2 ** 2)
            self._xt8 = self._xt16 / 2 ** 8;

        # se il calcolo del parametro ritorna 0 ma la frequenza di taglio e' != 0 => satura parametri a 1
        if Fcut_mHz_:
            if self._wt18 < 1:
                self._wt18 = 1
            if self._xt8 < 1:
                self._xt8 = 1

        self._Wt = self._wt18

    # Reset the accumulator of the filter
    def Reset(self):
        self._accumulator = 0

    def Preset(self, sample_: float):
        self._accumulator = sample_ * (2 ** self.CIF_LPF_IIR_SHIFTSTRAND)

    # calcolo filtro passabasso (la chiamata va fatta alla frequenza di campionamento definita nella init)
    def Filter(self, sample_):
        if self._Fcut_mHz:
            err = sample_ - (self._accumulator / (2 ** self.CIF_LPF_IIR_SHIFTSTRAND))
            self._accumulator += err * self._Wt;
            sample_ = self._accumulator / (2 ** self.CIF_LPF_IIR_SHIFTSTRAND)
        return sample_

    # Get the value of the filter
    def GetVal(self):
        val = self._accumulator/(2 ** self.CIF_LPF_IIR_SHIFTSTRAND)


