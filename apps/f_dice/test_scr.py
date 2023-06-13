from mb_common_lib.report import rpt_open, rpt_print
from f_dice.lib.tools import SinForm
import matplotlib.pyplot as plt


def MyPlot(r_, c_, i_, title_, x_, s1_, s2_, s3_):
    ptmp = plt.subplot(r_, c_, i_)
    plt.title = title_
    plt.grid(color='0.95')
    plt.plot(x_, s1_, 'm', label="output1")
    plt.plot(x_, s2_, 'y', label="output2")
    plt.plot(x_, s3_, 'g', label="output3")
    ptmp.set_xlabel("angle")
    ptmp.set_ylabel("values")
    plt.legend(title='Legend')


rpt_open("./debug.txt")
rpt_print("Zerocross simulation")
sinOutput1 = SinForm(0, 720)
sinOutput2 = SinForm(120, 720)
sinOutput3 = SinForm(240, 720)
MyPlot(3, 1, 1, "phases", sinOutput1[:, 0], sinOutput1[:, 1], sinOutput2[:, 1], sinOutput3[:, 1])

teta = sinOutput1[:, 0]
phu = sinOutput1[:, 1]
phv = sinOutput2[:, 1]
phw = sinOutput3[:, 1]
tsize = len(teta)
out_uv = [0 for i in range(tsize)]
out_vw = [0 for i in range(tsize)]
out_wu = [0 for i in range(tsize)]
zc_uv = [0 for i in range(tsize)]
zc_vw = [0 for i in range(tsize)]
zc_wu = [0 for i in range(tsize)]
iterator = [i for i in range(0, teta.size)]
zerocross_uv = 0
zerocross_vw = 0
zerocross_wu = 0

for val in iterator:
    out_uv[val] = phv[val] - phu[val]
    out_vw[val] = phw[val] - phv[val]
    out_wu[val] = phu[val] - phw[val]
    zc_uv[val] = int((phv[val] >= phu[val]))
    zc_vw[val] = int((phw[val] >= phv[val]))
    zc_wu[val] = int(phu[val] >= phw[val])
    if (zc_uv[val-1] == 0) and (zc_uv[val] == 1):
        zerocross_uv = teta[val - 1] % 360
    if zc_vw[val-1] == 0 and zc_vw[val] == 1:
        zerocross_vw = teta[val - 1] % 360
    if zc_wu[val-1] == 0 and zc_wu[val] == 1:
        zerocross_wu = teta[val - 1] % 360

MyPlot(3, 1, 2, "difference", teta, out_uv, out_vw, out_wu)

rpt_print("zerocross_uv: " + str(zerocross_uv))
rpt_print("zerocross_vw: " + str(zerocross_vw))
rpt_print("zerocross_wu: " + str(zerocross_wu))

MyPlot(3, 1, 3, "zerocross", teta, zc_uv, zc_vw, zc_wu)
plt.show()
