import math
import numpy as np

from tools import MyPlot

VEL_MS = 300
ANGOLO_DEG = 80
X0 = 0
H0 = 0
GRAV = 9.81

angolo_rad = np.deg2rad(ANGOLO_DEG)

Vx_mS = VEL_MS * math.sin(angolo_rad)
Vy_mS = VEL_MS * math.cos(angolo_rad)

tm_tot = (Vy_mS + np.sqrt((Vy_mS**2) + 2 * GRAV * H0))/GRAV
tm_v = np.arange(0,tm_tot,0.1)    # Squenza temporale fino a time totale

x_m = X0 + Vx_mS * tm_v
y_m = (Vy_mS * tm_v) + H0 - (0.5 * GRAV * (tm_v ** 2))

# p_m = np.sqrt((x_m ** 2) + (y_m ** 2))

plot = MyPlot(1,1,1,"moto parabolico",x_m,y_m)
plot.show()

print("tempo di volo: " + str(tm_tot))
print("distanza: " + str(x_m[-1]))
print("altezza: " + str(np.max(y_m)))