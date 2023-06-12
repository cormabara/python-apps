

def perc_err(val1_ : float, val2_: float):
    val = val1_ - val2_
    val = abs(val)
    if val1_ != 0:
        val = val / val1_
    elif val2_ != 0:
        val = val / val2_
    val = val * 100
    return val
