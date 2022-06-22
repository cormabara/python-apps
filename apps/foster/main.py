# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import math
import matplotlib.pyplot as plt
from foster import PowerData
from report import rpt_open, rpt_print, rpt_print_d
from conversions import iter_current_error, MAX_CURRENT_LSB


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    rpt_open();

    rpt_print("CHeck the error conversion for current using thi shift division")
    current = MAX_CURRENT_LSB
    iter_current_error()
    power_data = PowerData()

    power_data.iter_compare_calc(current)
    rpt_print("\n\nMAX - MIN\n\n")


    rpt_print("PIT")
    rpt_print_d("pit min[W]",min(power_data.theo_samples_pit()))
    rpt_print_d("pit max[W]",max(power_data.theo_samples_pit()))
    rpt_print_d("pit min   ",min(power_data.real_samples_pit()))
    rpt_print_d("pit max   ",max(power_data.real_samples_pit()))
    rpt_print_d("err% min  ",min(power_data.pit_errorperc_v))
    rpt_print_d("err% max  ",max(power_data.pit_errorperc_v))
    rpt_print("PIB")
    rpt_print_d("pib min[W]",min(power_data.pib_W))
    rpt_print_d("pib max[W]",max(power_data.pib_W))
    rpt_print_d("pib min   ",min(power_data.pib_cu))
    rpt_print_d("pib max   ",max(power_data.pib_cu))
    rpt_print_d("err% min  ",min(power_data.pib_errorperc_v))
    rpt_print_d("err% max  ",max(power_data.pib_errorperc_v))
    rpt_print("PDT")
    rpt_print_d("pdt min[W]",min(power_data.pdt_W))
    rpt_print_d("pdt max[W]",max(power_data.pdt_W))
    rpt_print_d("pdt min   ",min(power_data.pdt_cu))
    rpt_print_d("pdt max   ",max(power_data.pdt_cu))
    rpt_print_d("err% min  ",min(power_data.pdt_errorperc_v))
    rpt_print_d("err% max  ",max(power_data.pdt_errorperc_v))
    rpt_print("PDB")
    rpt_print_d("pdb min[W]",min(power_data.pdb_W))
    rpt_print_d("pdb max[W]",max(power_data.pdb_W))
    rpt_print_d("pdb min   ",min(power_data.pdb_cu))
    rpt_print_d("pdb max   ",max(power_data.pdb_cu))
    rpt_print_d("err% min  ",min(power_data.pdb_errorperc_v))
    rpt_print_d("err% max  ",max(power_data.pdb_errorperc_v))

    x = power_data.compare_range
    y1 = power_data.theo_samples_pit()
    y2 = power_data.real_samples_pit()
    y3 = power_data.pit_error_v
    y4 = power_data.error_perc_pit()

    # setting the axes at the centre
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(1, 1, 1)
    ax1.spines['left'].set_position('zero')
    ax1.spines['bottom'].set_position('zero')
    ax1.spines['right'].set_color('none')
    ax1.spines['top'].set_color('none')
    ax1.xaxis.set_ticks_position('bottom')
    ax1.yaxis.set_ticks_position('left')
    # plot the function
    plt.title("Power dissipated");
    plt.plot(x,y1, 'y')
    plt.plot(x,y2, 'g')
    plt.plot(x,y3, 'r')
    # show the plot
    plt.show()


    # setting the axes at the centre
    fig_err = plt.figure()
    ax_err = fig_err.add_subplot(1, 1, 1)
    ax_err.spines['left'].set_position('zero')
    ax_err.spines['bottom'].set_position('zero')
    ax_err.spines['right'].set_color('none')
    ax_err.spines['top'].set_color('none')
    ax_err.xaxis.set_ticks_position('bottom')
    ax_err.yaxis.set_ticks_position('left')
    # plot the function
    plt.title("Error %");
    plt.plot(x, y4, 'y')
    # show the plot
    plt.show()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
