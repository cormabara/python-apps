# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import sys
sys.path.append("../../tools")

import math
import sys
import matplotlib.pyplot as plt
import numpy as np
from kivy.uix.popup import Popup
import kivy.uix.label as kv_label

from foster import PowerData, DataType, DataFormat
from report import rpt_open, rpt_print, rpt_print_d, rpt_sep
from constants import MAX_CURRENT_LSB, print_start_data, pwm_max_duty,current_lsb2A_theo, current_A2lsb_theo
import easygui
import csv


# Calcolo del singolo valore sia teorico che reale
def calculate_single(curr_, cmp_):
    rpt_sep()
    rpt_print("SINGLE CALCULATION")
    rpt_print("current: " + str(curr_) + "[A]")

    curr_ = current_A2lsb_theo(curr_)
    rpt_print("current: " + str(curr_) + "[lsb]")
    
    curr_lsb = curr_
    power_data = PowerData(True)
    sample = power_data.calc_single(curr_lsb,cmp_)
    if sample:
        rpt_sep()
        rpt_print("for current(" + str(curr_lsb) + ")[lsb] and compare(" + str(cmp_) + "/" +str(pwm_max_duty) + ") the calc values are: ")
        dtype = DataType.PIT
        rpt_print("PIT\n\tReal(" + str(sample.get_value(dtype | DataFormat.data_real_WCU)) + ")\n\t"
            "theorical[W](" + str(sample.get_value(dtype | DataFormat.data_theo_W)) + ")\n\t"
            "theorical[WCU](" + str(sample.get_value(dtype | DataFormat.data_theo_WCU)) + ")\n\t"
            "Error[%](" + str(sample.get_value(dtype | DataFormat.theo_real_error_perc)) + ")\n\n")

        dtype = DataType.PDB
        rpt_print("PDB\n\tReal(" + str(sample.get_value(dtype | DataFormat.data_real_WCU)) + ")\n\t"
            "Theorical[W](" + str(sample.get_value(dtype | DataFormat.data_theo_W)) + ")\n\t"
            "Theorical[WCU](" + str(sample.get_value(dtype | DataFormat.data_theo_WCU)) + ")\n\t"
            "Error[%](" + str(sample.get_value(dtype | DataFormat.theo_real_error_perc)) + ")\n")

        dtype = DataType.PIB
        rpt_print("PIB\n\tReal(" + str(sample.get_value(dtype | DataFormat.data_real_WCU)) + ")\n\t"
            "Theorical[W](" + str(sample.get_value(dtype | DataFormat.data_theo_W)) + ")\n\t"
            "Theorical[WCU](" + str(sample.get_value(dtype | DataFormat.data_theo_WCU)) + ")\n\t"
            "Error[%](" + str(sample.get_value(dtype | DataFormat.theo_real_error_perc)) + ")\n")
        dtype = DataType.PDT
        rpt_print("PDT\n\t(" + str(sample.get_value(dtype | DataFormat.data_real_WCU)) + ")\n\t"
            "Theorical[W](" + str(sample.get_value(dtype | DataFormat.data_theo_W)) + ")\n\t"
            "Theorical[WCU](" + str(sample.get_value(dtype | DataFormat.data_theo_WCU)) + ")\n\t"
            "Error[%](" + str(sample.get_value(dtype | DataFormat.theo_real_error_perc)) + ")\n")


def calculate_iter():
    divider = 1000
    compare_iter = range(int(pwm_max_duty/divider)-1)
    compare_vals = [0 for i in compare_iter]
    power_data_v = [PowerData for i in compare_iter]

    rpt_print("\n\nCalculating....\n")
    val_t_pit = [0 for i in compare_iter]
    val_t_pib = [0 for i in compare_iter]
    val_t_pdt = [0 for i in compare_iter]
    val_t_pdb = [0 for i in compare_iter]
    val_r_pit = [0 for i in compare_iter]
    val_r_pib = [0 for i in compare_iter]
    val_r_pdt = [0 for i in compare_iter]
    val_r_pdb = [0 for i in compare_iter]
    errors_pit = [0 for i in compare_iter]
    errors_pib = [0 for i in compare_iter]
    errors_pdt = [0 for i in compare_iter]
    errors_pdb = [0 for i in compare_iter]
    for cc in compare_iter:
        compare_vals[cc] = divider + cc*divider
        power_data_v[cc] = PowerData(False)
        rpt_print("Calculate for compare = " + str(compare_vals[cc]))
        power_data_v[cc].calc_iter_current(compare_vals[cc])

        val_t_pit[cc] = (max(power_data_v[cc].get_samples(DataType.PIT|DataFormat.data_theo_WCU)))
        # val_t_pit[cc] = np.mean(np.array(power_data_v[cc].get_samples(DataType.PIT|DataFormat.data_theo_WCU)))

        val_t_pib[cc] = (max(power_data_v[cc].get_samples(DataType.PIB|DataFormat.data_theo_WCU)))
        val_t_pdt[cc] = (max(power_data_v[cc].get_samples(DataType.PDT|DataFormat.data_theo_WCU)))
        val_t_pdb[cc] = (max(power_data_v[cc].get_samples(DataType.PDB|DataFormat.data_theo_WCU)))
        val_r_pit[cc] = (max(power_data_v[cc].get_samples(DataType.PIT | DataFormat.data_real_WCU)))
        val_r_pib[cc] = (max(power_data_v[cc].get_samples(DataType.PIB | DataFormat.data_real_WCU)))
        val_r_pdt[cc] = (max(power_data_v[cc].get_samples(DataType.PDT | DataFormat.data_real_WCU)))
        val_r_pdb[cc] = (max(power_data_v[cc].get_samples(DataType.PDB | DataFormat.data_real_WCU)))
        errors_pit[cc] = (max(power_data_v[cc].get_samples(DataType.PIT | DataFormat.theo_real_error_perc)))
        errors_pib[cc] = (max(power_data_v[cc].get_samples(DataType.PIB | DataFormat.theo_real_error_perc)))
        errors_pdt[cc] = (max(power_data_v[cc].get_samples(DataType.PDT | DataFormat.theo_real_error_perc)))
        errors_pdb[cc] = (max(power_data_v[cc].get_samples(DataType.PDB | DataFormat.theo_real_error_perc)))

        rpt_print("pit r [m]% max  " + str(max(val_r_pit)))
        rpt_print("pit r [m]% min  " + str(min(val_r_pit)))

        rpt_print("pit err% max  " + str(max(errors_pit)) + "pit err% min  " + str(min(errors_pit)))
        rpt_print("pib err% max  " + str(max(errors_pib)) + "pib err% min  " + str(min(errors_pib)))
        rpt_print("pdt err% max  " + str(max(errors_pdt)) + "pdt err% min  " + str(min(errors_pdt)))
        rpt_print("pdb err% max  " + str(max(errors_pdb)) + "pdb err% min  " + str(min(errors_pdb)))
        rpt_print("Done")


    plt.subplot(2, 3, 1, ylabel="PIT / PDB")
    plt.plot(compare_vals, val_t_pit, 'r', label="pit_t")
    plt.plot(compare_vals, val_r_pit, 'g', label="pit_r")
    plt.plot(compare_vals, val_t_pdb, 'y', label="pdb_t")
    plt.plot(compare_vals, val_r_pdb, 'b', label="pdb_r")
    plt.legend(title='Legend')

    plt.subplot(2, 3, 2, title="negative current", ylabel="WCU")
    plt.plot(compare_vals, val_t_pib, 'r', label="pib_t")
    plt.plot(compare_vals, val_r_pib, 'g', label="pib_r")
    plt.plot(compare_vals, val_t_pdt, 'y', label="pdt_t")
    plt.plot(compare_vals, val_r_pdt, 'b', label="pdt_r")
    plt.legend(title='Legend')

    plt.subplot(2, 3, 3, title="Errors", xlabel="compare", ylabel="Error percentage")
    plt.plot(compare_vals, errors_pit,'r', label="pit")
    plt.plot(compare_vals, errors_pdb,'g', label="pdb")
    plt.plot(compare_vals, errors_pib,'y', label="pib")
    plt.plot(compare_vals, errors_pdt,'b', label="pdt")
    plt.legend(title='Legend')

    index = int(len(compare_iter)/2)
    pwd = power_data_v[index];

    plt.subplot(2, 3, 4, title="Current loop for compare = " + str(compare_vals[index]), xlabel="current", )
    plt.plot(pwd.GetCurrentValues(), pwd.get_samples(DataType.PIT|DataFormat.data_theo_WCU),'r', label="pit")
    plt.plot(pwd.GetCurrentValues(), pwd.get_samples(DataType.PDB|DataFormat.data_theo_WCU),'g', label="pdb")
    plt.plot(pwd.GetCurrentValues(), pwd.get_samples(DataType.PIB|DataFormat.data_theo_WCU),'y', label="pib")
    plt.plot(pwd.GetCurrentValues(), pwd.get_samples(DataType.PDT|DataFormat.data_theo_WCU),'b', label="pdt")
    plt.legend(title='Legend')

    plt.subplot(2, 3, 5, title="Error for compare = " + str(compare_vals[index]), xlabel="current", )
    plt.plot(pwd.GetCurrentValues(), pwd.get_samples(DataType.PIT|DataFormat.theo_real_error_perc),'r', label="pit")
    plt.plot(pwd.GetCurrentValues(), pwd.get_samples(DataType.PDB|DataFormat.theo_real_error_perc),'g', label="pdb")
    plt.plot(pwd.GetCurrentValues(), pwd.get_samples(DataType.PIB|DataFormat.theo_real_error_perc),'y', label="pib")
    plt.plot(pwd.GetCurrentValues(), pwd.get_samples(DataType.PDT|DataFormat.theo_real_error_perc),'b', label="pdt")
    plt.legend(title='Legend')


    # show the plot
    plt.grid(axis='x', color='0.95')
    plt.show()
    rpt_print("creating CSV")
    val = pwd.GetCurrentValues();
    theo = pwd.get_samples(DataType.PIT|DataFormat.data_theo_WCU)
    real = pwd.get_samples(DataType.PIT|DataFormat.data_real_WCU)
    err = pwd.get_samples(DataType.PIT|DataFormat.theo_real_error_perc)

    with open('./report.csv', 'w') as file:
        writer = csv.writer(file)
        for cc in pwd.current_iter:
            writer.writerow([str(val[cc]),str(theo[cc]), str(real[cc]), str(err[cc])])

    rpt_print("CSV created")
    #easygui.msgbox("End of application", title="")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    rpt_open()

    # iter_current_error()

    print_start_data()


    if len(sys.argv) == 3 and sys.argv[1] and sys.argv[2]:
        calculate_single(int(sys.argv[1]),int(sys.argv[2]))
        sys.exit()
    else:
        calculate_iter()

