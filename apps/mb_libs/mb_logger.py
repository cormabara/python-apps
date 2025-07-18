# Output file for the report
import datetime
import os
import string
from pprint import pprint

from mb_tools import SingletonMeta


class Logger(metaclass=SingletonMeta):
    rpt_filename = "report.txt"
    REPORT_SECTION_SEP = "____\n"

    def __init__(self, path_=".",fn_="report.txt"):
        self.rpt_filename = path_ + "/" + fn_
        if not os.path.exists(path_):
            os.makedirs(path_)

        out_file = open(self.rpt_filename, "w")
        out_file.write("This is the report file:\n")
        out_file.close()
        self.is_updated = True
        self.asReport = False

    def set_as_report(self):
        self.asReport = True

    def alarm(self, str_):
        self.print("##ALARM##" + " ##" + str_)

    def error(self, err_, str_):
        self.print("##ERR##: " + str(err_) + str_)

    def warning(self, str_):
        self.print("##WARN##" + str_)

    def info(self, str_):
        self.print("##INFO##" + str_)

    def debug(self, str_):
        self.print("##DBG##" + " ##" + str_)

    def sep(self):
        self.print(self.REPORT_SECTION_SEP)

    def print(self, v_):
        out_file = open(self.rpt_filename, "a")

        if not self.asReport:
            print("[" + str(datetime.datetime.now()) + "]", sep=" ", end="\t", file=out_file, flush=False)

        print(v_, sep=" ", end="\n", file=out_file, flush=False)
        print(v_)
        out_file.close()
        self.is_updated = True

    def pprint(self,v_):
        out_file = open(self.rpt_filename, "a")
        if not self.asReport:
            print("[" + str(datetime.datetime.now()) + "]", sep=" ", end="\t", file=out_file, flush=False)
        pprint(v_, out_file)
        pprint(v_)
        out_file.close()
        self.is_updated = True

    def print_d(self, name_, var_):
        str_ = name_ + ": \t" + str(var_) + "\t - \t" + hex(int(var_))
        self.print(str_)
        print(str_)

    def all(self):
        out_file = open(self.rpt_filename, "r")
        str_tmp = out_file.read()
        out_file.close()
        return str_tmp

    @property
    def updated(self):
        return self.is_updated

    def clr_updated(self):
        self.is_updated = False

