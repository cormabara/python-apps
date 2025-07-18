""" Inside this file the class to handle the error on the system (errors, warnings, ecc.. """
import numpy as np

from mb_logger import Logger
from mb_tools import SingletonMeta


def drverr_set(mod_, num_, par_):
    return mod_ + num_ << 8 + par_ << 16


def drverr_get_mod(err_):
    return err_ & 0xff


def drverr_get_num(err_):
    return (err_ >> 8) & 0xff


class MbException(metaclass=SingletonMeta):
    """ Class to handle the exception inside the system """
    glbl_error = None

    def __init__(self):
        pass

    def set_err(self, err_, str_):
        Logger().error(-1, str_)
        return err_

    def set_warn(self, str_):
        Logger().warning(str_)

    def set_alarm(self, num_, str_):
        err = num_
        Logger().alarm(str(num_) + " - " + str_)
        self.glbl_error = err
        return err

    def check_alarm(self):
        return self.glbl_error


def board_set_alarm(alarm_, str_="None"):
    MbException().set_alarm(alarm_, str_)

