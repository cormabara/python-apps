from pathlib import Path

from matplotlib import pyplot as plt
from pandas.io.common import file_exists

from mb_libs.mb_csv import MbCsvOscillo, array_to_csv
from mb_libs.mb_fourier import to_fourier
import sys


def get_filename_without_extension(file_path):
    # Use Path to handle the file path and get the stem (filename without extension)
    return Path(file_path).stem


def get_filename_extension(file_path):
    # Use Path to handle the file path and get the stem (filename without extension)
    return Path(file_path).suffix


def get_filename_path(file_path):
    return str(Path(filename).parent)


print(sys.argv[0])
filename = str(sys.argv[1])
channels = int(sys.argv[2])
channel = int(sys.argv[3])
if not file_exists(filename):
    print("File not found!")
    exit(1)

chns = [f"ch{ind}" for ind in range(1,channels+1)]

oscillo = MbCsvOscillo(filename)
oscillo.load_data_from_csv(chns)
data = oscillo.get_chn_values(chns[channel-1],None)

xf,yf,yff = to_fourier(data)
fpath = get_filename_path(filename)
fext1 = get_filename_extension(filename)
fout = get_filename_without_extension(filename)
fext2 = get_filename_extension(fout)
fout = get_filename_without_extension(fout)
fout = fpath + "/" + fout + "_output" + fext2 + fext1
array_to_csv(fout,xf,yff)

# Plot the results
plt.plot(xf, yff)
plt.grid()
plt.show()

