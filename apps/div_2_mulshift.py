# Output file for the report

import sys

shift = 0
print(sys.argv[0])
numerator = float(sys.argv[1])
reference = numerator
if sys.argv[2]:
	denominator = float(sys.argv[2])
	reference /=  denominator

for iter in range(1,32):
	reference *=  2
	shift += 1
	if reference:
		error = (reference - int(reference)) * 100 / reference
	if error < 20:	
		print("it (" + str(iter) + ")\t" \
				" mul (" + str(int(reference)) + ")\t" \
				" sh (" + str(shift) + ")\t" \
				" err% (" + str(error) + ")")
