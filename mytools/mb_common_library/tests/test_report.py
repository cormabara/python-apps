
from mb_common_lib import report


def test_report(path_):
    report.rpt_open(path_)
    report.rpt_print("this is a test for report file")
    report.rpt_sep()
    report.rpt_close()
