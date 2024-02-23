""" With this script is poosible to evaluate the error of a division with integers
    using a right shift to minimize error but staying into a 32 bit """

import sys

from tools import CheckUnsigned32, CheckUnsigned16, CheckSigned32
from types import S32

print(sys.argv[0])
numerator1 = float(sys.argv[1])
numerator2 = float(sys.argv[2])
divider1 = float(sys.argv[3])
divider2 = float(sys.argv[4])

for temp_iter in range(0, 31):
    factor = 1 << temp_iter
    division = ((numerator1 * numerator2) * factor) / (divider1 * divider2)
    if CheckSigned32(numerator1 * numerator2 * factor):
        print("overflow 32 bits on numerator: " + str(numerator1 * numerator2 * factor))
        break

    division_int = S32(division)
    error = (division - float(division_int)) * 100 / division
    print("<<" + str(temp_iter) + #": testing factor: " + str(factor) +
            " - value is: " + str(division_int) +
            " - error% is: " + str(error))

    if temp_iter == 14:
        break

for temp_speed in range(1, 2000000):
    result = float(division_int) * temp_speed
    if CheckSigned32(result):
        print("error overflow for speed: " + str(temp_speed))
        break

