from enum import IntEnum

from drv_err import drvErrSet
from range_limits import check_out_range

ID_ADC = 1

class Err_ID_ADC(IntEnum):
    adc_err_none = 0
    adc_err_inputOutOfRange = 1

class ADConv:

    def __init__(self, in_min_, in_max_,lsb_bit_range_):
        self.input_min = in_min_
        self.input_max = in_max_
        self.lsb_bit_range = 1 << lsb_bit_range_

    def convert(self, val_):
        if check_out_range(val_,self.input_min,self.input_max):
            drvErrSet(ID_ADC, Err_ID_ADC.adc_err_inputOutOfRange)

        return val_ * (2 ^ self.lsb_bit_range) / self.input_max
