import math
import matplotlib.pyplot as plt
import numpy as np

# 100 linearly spaced numbers
x = np.linspace(-2*np.pi,2*np.pi,100)

# the function, which is y = x^2 here
y1 = np.sin(x)
y2 = np.sin(x+(np.pi/3))
y3 = np.sin(x+((np.pi*2)/3))

# setting the axes at the centre
fig = plt.figure()
ax = fig.add_subplot(1, 1, 1)
ax.spines['left'].set_position('center')
ax.spines['bottom'].set_position('zero')
ax.spines['right'].set_color('none')
ax.spines['top'].set_color('none')
ax.xaxis.set_ticks_position('bottom')
ax.yaxis.set_ticks_position('left')

# plot the function
plt.title("Motor phases");
plt.plot(x,y1, 'r')
plt.plot(x,y2, 'g')
plt.plot(x,y3, 'b')

# show the plot
plt.show()
