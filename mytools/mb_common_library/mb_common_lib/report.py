# Output file for the report

REPORT_SECTION_SEP = "---------------------------------------------\n"


def rpt_open(path_):
    out_file = open("./report.txt", "w")
    out_file.close()


def rpt_print_d(str_,var_):
    out_file = open("./report.txt", "a")
    print(str_ + ": \t" + str(var_) + "\t - \t" + hex(int(var_)))
    out_file.write(str_ + ": \t" + str(var_) + "\t - \t" + hex(int(var_)) + "\n")
    out_file.close()


def rpt_print(str_):
    out_file = open("./report.txt", "a")
    print(str_)
    out_file.write(str_+"\n")
    out_file.close()


def rpt_sep():
    rpt_print(REPORT_SECTION_SEP)


def rpt_close():
    pass
