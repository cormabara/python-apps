"""
Library file with all defines and macro about data types
"""
import numpy
import numpy as np

from mb_logger import Logger

drverr_dt = int


U32_MAX = (2 ** 32) - 1  # Max for unsigned 32 integer
S32_MAX = (2 ** 31) - 1  # Max for signed 32 integer
S32_MIN = -((2 ** 31) - 1)  # Max for signed 32 integer

U16_MAX = (2 ** 16) - 1  # Max for unsigned 32 integer
S16_MAX = (2 ** 15) - 1  # Max for signed 32 integer
S16_MIN = -((2 ** 15) - 1)  # Max for signed 32 integer

U8_MAX = (2 ** 8) - 1  # Max for unsigned 32 integer
S8_MAX = (2 ** 7) - 1  # Max for signed 32 integer
S8_MIN = -((2 ** 7) - 1)  # Max for signed 32 integer


def U32(v_):
    return int(v_ + (1 << 32))


def S32(v_):
    return int(v_)


def U16(v_):
    return int(v_ + (1 << 16))


def S16(v_):
    return int(v_) & 0x0000ffff


def U8(v_):
    return int(v_ + (1 << 8))


def S8(v_):
    return int(v_) & 0xff


def _check_bit_overflow(d_, numbits_, signed_):
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


def check_u32(d_):
    return not _check_bit_overflow(d_, 32, False)


def check_s32(d_):
    return not _check_bit_overflow(d_, 32, True)


def check_u16(d_):
    return not _check_bit_overflow(d_, 16, False)


def check_s16(d_):
    return not _check_bit_overflow(d_, 16, True)


def set_s32(v_) -> numpy.int32:
    if not check_s32(v_):
        Logger().error(-2, "set_s32 overflow")
    return np.int32(v_)


def dm_sign(v_):
    return 1 if v_ > 0 else -1


def dm_abs(v_):
    return v_ if v_ > 0 else -v_
