# Calcolo della potenza

Il calcolo della potenza parte dal calcolo della potenza apparente S dove:

$$
S = \sqrt(P^2 + Q^2)
$$
Dove:

S: potenza apparente

P: Potenza attiva

Q: Potenza Reattiva

suppnendo che tra tensione e corrente sinusoidali ci sia un angolo j (fi) abbiamo che:
$$
P = V * I * cos(\phi)
$$
$$
Q = v*I * sin(\phi)
$$

Dove V e I sono i valori rms di tensione e corrente 

$$
V_{rms} = V_{max} / \sqrt(2)
$$
$$
I_{rms} = I_{max} / \sqrt(2)
$$

Quindi considerando il nostro caso:
Irms viene già calcolata sotto irq, nella fattispecie vedi la variabile can [0x600322]
Vrms invece deve essere calcolato come la tensione di bus per il tempo di on:
$$
    T_{on} = 2 * \bmod(cmp_u - cmp_v) * PWMTICK - (2 * DEADTIME) + (2 * HWDELAY) 
$$

Quindi 

La Vmax è uguale alla Vbus e viene applicata per un Ton ogni ciclo di PWM quindi:

$$
V_{uv} = T_{on} * V_{bus} / (2 * MAXPWM * PWMTICK)
$$
