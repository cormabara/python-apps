import time

from config import MbConfig


class SysTimerReal:

    def __init__(self, timeout_ms_ = 0):
        self.timeout_ns = 0
        self.start_ns = 0
        self.end_ns = 0


        self.start(timeout_ms_)

    def expired(self):
        return True if time.monotonic_ns() >= self.end_ns else False

    def time(self):
        return time.monotonic_ns() - self.start_ns

    def start(self, timeout_ms_: int = 0):
        if timeout_ms_ != 0:
            self.timeout_ns = timeout_ms_ * 1000000
        tt = self.time()
        self.start_ns = time.monotonic_ns()
        self.end_ns = self.start_ns + self.timeout_ns
        return tt

    def CheckLoop(self):
        retval = self.expired()
        if retval is True:
            self.start()
        return retval

class SysTimer:

    def __init__(self, timeout_ms_=0):
        self.timeout_us = 0
        self.start_us = 0
        self.end_us = 0
        self.start(timeout_ms_)

    def monotonic_us(self):
        return MbConfig().sys_timer_us

    def expired(self):
        return True if self.monotonic_us() >= self.end_us else False

    def time(self):
        return self.monotonic_us() - self.start_us

    def start(self, timeout_ms_: int = 0):
        if timeout_ms_ != 0:
            self.timeout_us = timeout_ms_ * 1000
        tt = self.time()
        self.start_us = self.monotonic_us()
        self.end_us = self.start_us + self.timeout_us
        return tt

    def CheckLoop(self):
        retval = self.expired()
        if retval is True:
            self.start()
        return retval
