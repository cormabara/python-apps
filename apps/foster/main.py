# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import sys
sys.path.append("../../tools")

import math
import sys
import matplotlib.pyplot as plt
import numpy as np

from foster import PowerData, PowerSample, DataType, DataFormat
from report import rpt_open, rpt_print, rpt_print_d, rpt_sep
from constants import MAX_CURRENT_LSB, MIN_CURRENT_LSB, print_start_data, pwm_max_duty,current_lsb2A_theo, current_A2lsb_theo
import csv
import pandas

def calculate_from_arrays(currents_, compares_):

    pwd = PowerData()
    pwd.CalcVectors(currents_, compares_)

    plt.subplot(3, 2, 1, title="INPUT")
    plt.plot(pwd.samples, pwd.get_current(), 'm', label="current")
    plt.plot(pwd.samples, pwd.get_compare(), 'b', label="compares")
    plt.legend(title='Legend')

    plt.subplot(3, 2, 3, title="DATA REAL")
    plt.plot(pwd.samples, pwd.get_values(DataType.PIT | DataFormat.data_real_WCU), 'r', label="pit_r")
    plt.plot(pwd.samples, pwd.get_values(DataType.PDB | DataFormat.data_real_WCU), 'g', label="pdb_r")
    #plt.plot(samples, pib_v_r, 'y', label="pib_r")
    #plt.plot(samples, pdt_v_r, 'b', label="pdt_r")
    plt.legend(title='Legend')

    plt.subplot(3, 2, 4, title="DATA THEORICAL")
    plt.plot(pwd.samples, pwd.get_values(DataType.PIT | DataFormat.data_theo_W), 'r', label="pit_t")
    plt.plot(pwd.samples, pwd.get_values(DataType.PDB | DataFormat.data_theo_W), 'g', label="pdb_t")
    #plt.plot(samples, pib_v_t, 'y', label="pib_t")
    #plt.plot(samples, pdt_v_t, 'b', label="pdt_t")
    plt.legend(title='Legend')

    plt.subplot(3, 2, 5, title="COMPARE REAL-THEO")
    plt.plot(pwd.samples, pwd.get_values(DataType.PIT | DataFormat.data_real_WCU), 'r', label="pit_r")
    plt.plot(pwd.samples, pwd.get_values(DataType.PDB | DataFormat.data_real_WCU), 'g', label="pdb_r")
    plt.plot(pwd.samples, pwd.get_values(DataType.PIT | DataFormat.data_theo_WCU), 'r', label="pit_t", linestyle='dashed')
    plt.plot(pwd.samples, pwd.get_values(DataType.PDB | DataFormat.data_theo_WCU), 'g', label="pdb_t", linestyle='dashed')
    #plt.plot(samples, pib_v_r, 'y', label="pib_r")
    #plt.plot(samples, pdt_v_r, 'b', label="pdt_r")
    plt.legend(title='Legend')

    plt.subplot(3, 2, 6, title="ERROR %")
    plt.plot(pwd.samples, pwd.get_values(DataType.PIT | DataFormat.data_error), 'r', label="pit_e")
    plt.plot(pwd.samples, pwd.get_values(DataType.PDB | DataFormat.data_error), 'g', label="pdb_e")
    #plt.plot(samples, pib_v_error, 'y', label="pib_e")
    #plt.plot(samples, pdt_v_error, 'b', label="pdt_e")
    plt.legend(title='Legend')

    plt.grid(axis='x', color='0.95')
    plt.show()



def calculate_from_csv(filename_):
    rpt_print("\nCALCULATE FROM FILE: " + filename_)
    current = pandas.read_csv(filename_,usecols =[0],header=12 ).to_numpy()
    compare = pandas.read_csv(filename_,usecols =[1],header=12 ).to_numpy()
    calculate_from_arrays(current, compare)

def calculate_from_sin():
    rpt_print("\nCALCULATE FROM ARRAY")
    samples = np.arange(0, 1000, 1)  # Get x values of the sine wave
    compare_v = ((pwm_max_duty / 2)-1) * np.sin( (samples % 360) * np.pi / 180)
    compare_v += (pwm_max_duty / 2)
    #compare_v = [(3*pwm_max_duty / 4) for i in samples]

    samples = np.arange(1000, 2000, 1)  # Get x values of the sine wave
    current_v = (((MAX_CURRENT_LSB - MIN_CURRENT_LSB) / 2)-1) * np.sin((samples % 360) * np.pi / 180)
    current_v += (MAX_CURRENT_LSB + MIN_CURRENT_LSB) / 2
    #current_v = [(3*MAX_CURRENT_LSB / 4) for i in samples]
    calculate_from_arrays(current_v, compare_v)

def calculate_from_tooth():
    rpt_print("\nCALCULATE FROM ARRAY")
    samples = np.arange(0, pwm_max_duty, pwm_max_duty/1000)  # Get x values of the sine wave
    compare_v = samples
    samples = np.arange( MIN_CURRENT_LSB, MAX_CURRENT_LSB, (MAX_CURRENT_LSB-MIN_CURRENT_LSB) / 1000 )  # Get x values of the sine wave
    current_v = samples
    calculate_from_arrays(current_v, compare_v)


# Calcolo del singolo valore sia teorico che reale
def calculate_single(curr_, cmp_):
    rpt_sep()
    rpt_print("SINGLE CALCULATION")
    rpt_print("current: " + str(curr_) + "[lsb]")
    rpt_print("current: " + str(current_lsb2A_theo(curr_)) + "[A]")
    
    curr_lsb = curr_
    power_data = PowerData()
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
    return power_data
    

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    rpt_open()

    # iter_current_error()

    print_start_data()

    if len(sys.argv) == 3 and sys.argv[1] and sys.argv[2]:
        calculate_single(int(sys.argv[1]),int(sys.argv[2]))
    elif len(sys.argv) == 2 and sys.argv[1]:
        calculate_from_csv(sys.argv[1])
    else:
        calculate_from_tooth()

    rpt_print("END")