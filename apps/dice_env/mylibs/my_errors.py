from report import MyReport
from tools import SingletonMeta


class SysErr(metaclass=SingletonMeta):
    glbl_error = None

    def __init__(self):
        pass

    def set_int_err(self, num_, str_):
        err = num_
        MyReport().rpt_print("INT-ERR: " + str(num_) + " - " + str_)
        return err

    def set_alarm(self, num_, str_):
        err = num_
        MyReport().rpt_print("ALARM: " + str(num_) + " - " + str_)
        # self.glbl_error = err
        return err

    def check_alarm(self):
        return self.glbl_error