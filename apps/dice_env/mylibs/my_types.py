"""
Library file with all defines and macro about data types
"""

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
