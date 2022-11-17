import time

class SysTimer:

    def __init__(self, timeout_ms_):
        self.timeout_ns = timeout_ms_*1000000
        self.end = time.monotonic_ns() + self.timeout_ns

    def Check(self):
        return True if time.monotonic_ns() >= self.end else False

    def Start(self, timeout_ms_ = 0):
        if timeout_ms_ is not 0:
            self.timeout_ns = timeout_ms_ * 1000000
        self.end = time.monotonic_ns() + self.timeout_ns

    def CheckLoop(self):
        retval = self.Check()
        if retval is True:
            self.Start()
        return retval
