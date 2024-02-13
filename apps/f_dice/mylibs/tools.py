import numpy
import numpy as np
import math

from matplotlib import pyplot as plt

from f_dice.lib.types import U32_MAX, S32_MAX, S32_MIN


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
    val = [(ind/range_)*(vend_-vstart_) + vstart_ for ind in range(0, range_)]
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
    return (int(val_) + (1 << (shift_ - 1))) >> shift_


def _CheckBitOverflow(d_, numbits_, signed_):
    """Function to check overflow, if overflow of the format return true"""
    if signed_:
        if d_ > ((2 ** (numbits_ - 1)) - 1):
            return True
        elif d_ < -((2 ** (numbits_ - 1)) - 1):
            return True
    else:
        if abs(d_) > ((2 ** numbits_) - 1):
            return True

    return False


def CheckUnsigned32(d_):
    return _CheckBitOverflow(d_, 32, False)


def CheckSigned32(d_):
    return _CheckBitOverflow(d_, 32, True)


def CheckUnsigned16(d_):
    return _CheckBitOverflow(d_, 16, False)


def CheckSigned16(d_):
    return _CheckBitOverflow(d_, 16, True)


def CheckIntOverflow(d_, numbits_):
    if abs(d_) > ((2 ** (numbits_ - 1)) - 1):
        return True
    else:
        return False


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
