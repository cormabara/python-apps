import time


class SysTimer:

    def __init__(self, timeout_ms_ = 0):
        self.timeout_ns = 0
        self.start_ns = 0
        self.end_ns = 0


        self.start(timeout_ms_)

    def Check(self):
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
        retval = self.Check()
        if retval is True:
            self.start()
        return retval
