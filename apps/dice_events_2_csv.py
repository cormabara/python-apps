"""This macro convert the binary file of events created by dice system into a readable csv format
"""
import sys
from os.path import exists
import struct

import numpy as np



class Event:
    def __init__(self,time_,code_,data_):
        self.time = time_
        self.code = code_
        self.data = data_
        self.tot_time_s = int(self.time / 100000000)
        self.tot_time_m = int(self.tot_time_s / 60)
        self.tot_time_h = int(self.tot_time_m / 60)
        self.tot_time_d = int(self.tot_time_h / 24)

        self.time_h = self.tot_time_h % 24
        self.time_m = self.tot_time_m % 60
        self.time_s = self.tot_time_s % 60
        self.time_ms = int((self.time / 100000) % 1000)
        self.time_us = int((self.time / 100) % 1000)

        self.time_str = (str(self.tot_time_d) + "." + str(self.time_h) + "." + str(self.time_m) + "." + str(self.time_s) +
                         "." + str(self.time_ms) + "." + str(self.time_us))

    def cvs_total(self):
        return [self.time, self.time_str, self.tot_time_h, self.tot_time_m, self.tot_time_s, format(self.code,'#06x'), str(self.data)]

    def cvs_time_id(self):
        return [self.time, self.tot_time_d,self.time_h,self.time_m,self.time_s,self.time_ms,self.time_us, format(self.code,'#06x')]


print(sys.argv[0])
fn = str(sys.argv[1])
DUMMY_CODE = 65535


if not exists(fn):
    print("The file " + fn + "not exist")

# Define the record format (little-endian: <, int: I, float: f, short: h)
record_format = "<QH22B"
record_size = struct.calcsize(record_format)  # Calculate the size of one record

with open(fn, "rb") as file:
    records = list()
    while chunk := file.read(record_size):  # Read one record at a time
        if len(chunk) < record_size:
            break  # Stop if there's incomplete data at the end
        record = struct.unpack(record_format, chunk)  # Unpack the binary data
        event = Event(record[0],record[1],record[2:])
        if event.code == DUMMY_CODE:
            break
        records.append(event)

    #print(records)
    import csv

    with open("../outputs/output.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["TIMESTAMP","DD","HH","MM","SS","MS","US","CODE"])
        for it in records:
            writer.writerow(np.array(it.cvs_time_id()))  # Write multiple rows


