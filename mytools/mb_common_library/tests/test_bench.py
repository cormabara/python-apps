
from mb_common_lib import report
from mb_common_lib.types import S32_MIN, S32_MAX


def test_lib(path_):
    report.rpt_open(path_)
    report.rpt_print("this is a test for report file")
    report.rpt_sep()
    pippo = S32_MIN
    pluto = S32_MAX
    report.rpt_print(pippo)
    report.rpt_print(pluto)
    report.rpt_close()


test_lib("./")
