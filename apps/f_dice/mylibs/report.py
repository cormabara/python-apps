# Output file for the report
import string

REPORT_SECTION_SEP = "---------------------------------------------\n"
rpt_filename: string = ""


def rpt_open(path_=".", filen_="report.txt"):
    global rpt_filename
    rpt_filename = path_ + "/" + filen_
    rpt_file = open(rpt_filename, "w")
    rpt_file.write("This is the report file: ")
    rpt_file.close()


def _rpt_print(str_):
    global rpt_filename
    if rpt_filename:
        rpt_file = open(rpt_filename, "a")
        print(str_)
        rpt_file.write(str_ + "\n")
        rpt_file.close()


def rpt_print(str_):
    _rpt_print(str_)


def rpt_print_d(str_, var_):
    str_ = str_ + ": \t" + str(var_) + "\t - \t" + hex(int(var_))
    _rpt_print(str_)


def rpt_sep():
    _rpt_print(REPORT_SECTION_SEP)


def rpt_close(self):
    pass


class MyReport:
    rpt_filename = "report.txt"
    REPORT_SECTION_SEP = "---------------------------------------------\n"

    def __init__(self, path_=".", filen_="report.txt"):
        self.rpt_filename = path_ + "/" + filen_
        out_file = open(self.rpt_filename, "w")
        out_file.write("This is the report file: ")
        out_file.close()

    def rpt_print_d(self, str_, var_):
        str_ = str_ + ": \t" + str(var_) + "\t - \t" + hex(int(var_))
        self.rpt_print(str_)

    def rpt_print(self, str_):
        out_file = open(self.rpt_filename, "a")
        print(str_)
        out_file.write(str_ + "\n")
        out_file.close()

    def rpt_sep(self):
        self.rpt_print(self.REPORT_SECTION_SEP)

    def rpt_close(self):
        pass
