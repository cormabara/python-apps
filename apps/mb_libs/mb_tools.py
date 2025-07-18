import threading
from collections import deque

import numpy
import numpy as np
import math

from matplotlib import pyplot as plt

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonMetaOld(type):
    """ This is the meta class to create a singleton class """

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance

        return cls._instances[cls]




def SinForm(phase_, range_):
    angleDeg = np.arange(0, range_, 1)
    angle = numpy.deg2rad(angleDeg)
    val = np.sin(angle + numpy.deg2rad(phase_))
    #   out = [time, val]
    out = np.vstack((angleDeg, val)).T
    return out


def Ramp(vstart_, vend_, range_):
    """ Create a ramp using vstart_ and vend_ as starting and ending vertical value.
        range is the number of points """
    val = [(ind / range_) * (vend_ - vstart_) + vstart_ for ind in range(0, range_)]
    return val


def DivToMulshift(value_):
    shift = 0
    reference = 1 / value_

    for iter in 64:
        reference <<= 1
        shift += 1
        error = (reference - int(reference)) * 100 / reference
        print("iteration (" + str(iter) + ") mul (" + str(int(reference)) + ") rshift (" + str(shift) + ")")


def shift_dx(val_: int, sh_: int):
    return val_ >> sh_


def shift_sx(val_: int, sh_: int):
    return int(val_) << int(sh_)


def divshx(val_, shift_):
    return (np.int32(val_) + (1 << (shift_ - 1))) >> shift_

def divshxu(val_, shift_):
    """ divisione unsigned per potenze di 2 con approssimazione +/- 0.5 (6[cycles]) (DIVision by right-SHift 
        with approXimation, dividendo Unsigned) """
    val_ = np.int32(val_)
    return (val_ + (1 << (shift_ - 1))) >> shift_


def MyPlot(r_, c_, i_, title_, x_, s1_, s2_=None, s3_=None, s4_=None):
    ptmp = plt.subplot(r_, c_, i_)
    plt.title = title_
    plt.grid(color='0.95')
    if s1_ is not None:
        plot1, = plt.plot(x_, s1_, 'm', label="out1")
    if s2_ is not None:
        plt.plot(x_, s2_, 'y', label="out2")
    if s3_ is not None:
        plt.plot(x_, s3_, 'g', label="out3")
    if s4_ is not None:
        plt.plot(x_, s4_, 'r', label="out3")
    ptmp.set_xlabel("x")
    ptmp.set_ylabel("values")
    plt.legend(title=title_)
    return plt


def perc_err(val1_: float, val2_: float):
    val = val1_ - val2_
    val = abs(val)
    if val1_ != 0:
        val = val / val1_
    elif val2_ != 0:
        val = val / val2_
    val = val * 100
    return val


def div_sqr3(value_):
    # rv = val_ / sqrt(3) = val_ * 0,5773502691896258
    # rv ~= val_ * 2365 / 4096   ==> errore = +0,00733[%]
    # rv ~= val_ * 591 / 1024    ==> errore = -0,03496[%]
    # rv ~= val_ * 37 / 64       ==> errore = +0,13419[%]
    return divshx((value_ * 2365), 12)


def rms_val(fun_):
    """ Calculate the rms value of a array of values """
    return np.sqrt(np.mean(fun_**2))

def sin_rms_val(fun_):
    """ Calculate the rms value of a array of values """
    return np.sqrt(np.mean(fun_**2))

def rms_val_from_pk(pkval_):
    """ Get the rms value using the peak value of the waveform """
    return pkval_ * math.sqrt(2) /2


def rms_2_peak(rms_):
    """ Get the peak value of sin waveform from the rms """
    return rms_ * math.sqrt(2)


def star_2_triangle(rms_):
    """ Convert rms value from star to triangle """
    return rms_ * math.sqrt(3)


def triangle_2_star(rms_):
    """ Convert rms value from triagnle to star """
    return rms_ / math.sqrt(3)


def rpm_2_rps256(rpm_):
    rps256 = rpm_ * 256 / 60
    return rps256


def rps256_2_rpm(rps256_):
    rpm = rps256_*60/256
    return rpm


