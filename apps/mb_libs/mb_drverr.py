"""
File con la gestione degli errori interni
"""
from collections import deque

err_stack_deep = 32
err_stack = deque([0 for i in range(err_stack_deep)], maxlen=err_stack_deep)


def drvErrCompose(id_, err_, par_):
    return id_ + (err_ << 8) + (par_ << 16)


def drvErrSet(id_, err_, par_=0):
    err_stack.append(drvErrCompose(id_, err_, par_))


def drvErrGetStack(self):
    return self.err_stack