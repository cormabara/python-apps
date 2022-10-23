# Output file for the report
from report import rpt_print_d, rpt_print, rpt_sep

def DivToMulshift(value_):
    shift = 0
    reference = 1 / value_

    for iter in 64:
        reference <<= 1
        shift += 1
        error = (reference - int(reference)) * 100 / reference
        print("iteration (" + str(iter) + ") mul (" + str(int(reference)) + ") rshift (" + str(shift) + ")")


def CheckIntOverflow(d_, numbits_):
    if abs(d_) > ((2 ** (numbits_-1)) - 1):
        # rpt_print("int32 overflow: " + str(d_))
        return True
    else:
        return False
