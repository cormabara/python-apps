# THis script test a generic PID with a waveform input 

import sys
import keyboard
import msvcrt
import matplotlib.pyplot as plt
from f_dice.lib.report import rpt_open,rpt_print,rpt_close
from f_dice.lib.my_pid import MyPid

SAMPLES = 40


def CheckKey():
    if msvcrt.kbhit():
        key_stroke = msvcrt.getch()
        return key_stroke   # will print which key is pressed

def guiInput():
    key = CheckKey()
    if key:
        if key == "p":
            val = input("insert kp")
            pid.kp = val
            return False
        if key == "i":
            val = input("insert ki")
            pid.ki = val
            return False
        if key == "q":
            return True


rpt_open("./pid_test.txt")
rpt_print(sys.argv[0])

vref = input("Insert reference")
vfbk = 0

pid = MyPid()
pid.setProportional(1, 0)
pid.setIntegral(1, 0)
pid.antiwindup_max = 100
pid.antiwindup_min = 0

x = [i for i in range(0,SAMPLES)]
output = [0 for i in range(0,SAMPLES)]
index = 0

print("Filter")
tmp = plt.subplot(1, 1, 1)
plt.grid(color='0.95')
tmp.set_xlabel("time[s]")
tmp.set_ylabel("value")
plt.legend(title='Legend')
plt.ion()
fig = plt.figure()

plt.plot(x, output, 'm', label="output")

cmdexit = False

while not cmdexit:
    guiInput()
    output[index] = pid.output(vref - vfbk)
    if index == SAMPLES:
        shift = 1;
        for shift in SAMPLES-1:
            output[shift-1] = output[shift]
    else:
        index += 1
    fig.canvas.draw()
    fig.canvas.flush_events()

rpt_close()