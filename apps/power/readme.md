# Calcolo della potenza

Il calcolo della potenza parte dal calcolo della potenza apparente S dove:

$S = \sqrt(P^2 + Q^2)$

Dove:

S: potenza apparente

P: Potenza attiva

Q: Potenza Reattiva

supponendo che tra tensione e corrente sinusoidali ci sia un angolo j (fi) abbiamo che:
$P = V * I * cos(\phi)$
$Q = V*I * sin(\phi)$

Dove V e I sono i valori rms di tensione e corrente calcolati come 

$V_{rms} = V_{max} / \sqrt(2)$
$I_{rms} = I_{max} / \sqrt(2)$

Quindi considerando il nostro caso:
Irms viene già calcolata sotto irq, nella fattispecie vedi la variabile can [0x600322]
Vrms invece deve essere calcolato come la tensione di bus per il tempo di on:

$T_{on} = 2 * \bmod(cmp_u - cmp_v) * PWMTICK - (2 * DEADTIME) + (2 * HWDELAY)$

Quindi 

La Vmax è uguale alla Vbus e viene applicata per un Ton ogni ciclo di PWM quindi:

$V_{uv} = T_{on} * (V_{bus})^2 / (2 * MAXPWM * PWMTICK)$

Quindi la potenza apparente è:
    
$S = 3 * V_{ph-N} * I_{ph}$ dove: $V_{ph-N}$ è la tensione di fase calcolata ripetto al centro stella mentre $I_{ph}$ è la corrente di fase (sempre la stessa a prescindere da centro stella o triangolo)

Dato che $V_{ph_N}=V_{ph-ph}/\sqrt(3)$ con la $V_{ph-ph}=V_{uv}$ 

Abbiamo che:

$S=\sqrt(3)*V_{ph-ph}*I_{ph}$

La potenza attiva invece viene calcolata come la potenza attiva del sistema calcolata come il prodotto di tensione e corrente applicate dall'anello di corrente che applica due tensioni $V_d$ e $V_q$ e rilegge due correnti $I_d$ e $I_q$ dove "d" e "q" sono due componenti ortogonali del sistema quindi:

$P = (V_{d-ref}*I_{d-fbk})+(V_{q-ref}*I_{q-fbk})$

Note le due potenze P e S rimane da calcolare $cos(\phi)$:

Ora $P=S*cos(\phi)$  quindi   $\cos \phi =\frac{P}{S}$

# Ottimizzazione dei calcoli
### Calcolo del $cos(\phi)$
Vediamo di ottimizzare le operazioni per il calcolo del $cos(\phi)$ :

$$
\begin{aligned}
cos(\phi) = \frac{P}{S} \\
&= \frac{(V_{d[V]}*I_{d[A]})+(V_{q[V]}*I_{q[A]})}{\sqrt(3)*V_{ph[V]}*I_{ph[A]}} \\
\\
&= \frac{(V_{d[lsb]}*lsb2V*I_{d[lsb]}*lsb2A)+(V_{q[lsb]}*lsb2V*I_{q[lsb]}*lsb2A)}{\sqrt(3)*V_{ph[lsb]}*lsb2V*I_{ph[lsb]}*lsb2A} \\
\\
&= \frac{[(V_{d[lsb]}*I_{d[lsb]})+(V_{q[lsb]}*I_{q[lsb]})]*(lsb2V*lsb2A)}{(\sqrt(3)*V_{ph[lsb]}*I_{ph[lsb]}) * (lsb2V*lsb2A)} \\
\\
&= \frac{(V_{d[lsb]}*I_{d[lsb]})+(V_{q[lsb]}*I_{q[lsb]})}{(\sqrt(3)*V_{ph[lsb]}*I_{ph[lsb]})}
\end{aligned}
$$

In questo modo evitiamo di eseguire la conversione in volt e in ampere dato che la maggior parte delle grandezze è in LSB. QUindi abbiamo che:

$P_{lsb}=(V_{d[lsb]}*I_{d[lsb]})+(V_{q[lsb]}*I_{q[lsb]})$

mentre 

$S_{lsb}=(\sqrt(3)*V_{ph[lsb]}*I_{ph[lsb]})$ 

Vediamo ora le singole grandezze in gioco:
- $V_d$, $V_q$ sono disponibili su dice in lsb
- $I_d$ e $I_q$ sono già disponibili in lsb 
- $I_{ph[lsb]}$ è già disponibile in lsb

Rimane da vedere la $V_{ph[lsb]}$ che è calcolata partendo dalla Vbus
L'agoritmo di conversione da volt a lsb per Vd e Vq è:

$$
V_{d[V]}=\frac{V_{d[lsb]}*V_{bus[V]}}{lsb2V}
$$
quindi volendo fare la conversione opposta:

$$
V_{d[lsb]}=\frac{V_{d[V]}*lsb2V}{V_{bus[V]}}
$$

dove $lsb2V=V_{bus[V]}/(2^{14})$

Applicando la formula nel calcolo della Vbus in lsb di Vd dobbiamo sostituire $V_{d[V]}$ con $V_{bus[V]}$ quindi 

$V_{ph-ph[lsb]} = T_{on} * (V_{bus[lsb]})^2 / PWMTIME$

$V_{ph-ph[lsb]} = T_{on} * (V_{bus[lsb]})^2 / (2 * MAXPWM * PWMTICK)$


### Ottimizzazione del calcolo della tensione di fase

$T_{on} = 2 * \bmod(cmp_u - cmp_v) * PWMTICK - (2 * DEADTIME) + (2 * HWDELAY)$

Quindi 

La Vmax è uguale alla Vbus e viene applicata per un Ton ogni ciclo di PWM quindi:

$$
\begin{aligned}
V_{uv[lsb]} = \\
&= \frac{T_{on} * (V_{bus[lsb]})^2}{(2 * MAXPWM * PWMTICK)} \\
\\
&= \frac{T_{on} * (V_{bus[lsb]})^2}{2 * MAXPWM * PWMTICK} \\
\\
&= \frac{(2 * (\bmod(cmp_u - cmp_v) * PWMTICK) - (2 * DEADTIME) + (2 * HWDELAY))*(V_{bus[lsb]})^2}{2 * MAXPWM * PWMTICK} \\
\\
&= \frac{2*((\bmod(cmp_u - cmp_v)*PWMTICK) - DEADTIME + HWDELAY)*(V_{bus[lsb]})^2}{2 * MAXPWM * PWMTICK}\\
\\
&= ((\bmod(cmp_u - cmp_v)*PWMTICK) - DEADTIME + HWDELAY) * \frac{2*(V_{bus[lsb]})^2}{2*MAXPWM*PWMTICK}
\end{aligned}
$$

> Da notare che eseguendo il calcolo in lsb abbiamo anche una maggiore risoluzione
    
## Algoritmo
Guardando come è messo il software la cosa migliore è avere i campioni sotto interrupt:
Vd,Id,Vq,Iq sono tutti disponibili sotto irq dovrebbero solo essere salvati in una lista come quella della temperatura
Va implementata una lista come quella della stima della temepratura con i seguenti dati campionati sotto irq:

CMP_U = DICE\_data_import(fname, varnum ); 0x660318 
CMP_V = DICE\_data_import(fname, varnum ); 0x660319
Vbus = DICE\_data\_import(fname, varnum ); 0x210104
Iu_rms = DICE\_data_import(fname, varnum ); 0x660322
Vd_ref = DICE\_data_import(fname, varnum ); 0x660310
Vq_ref = DICE\_data_import(fname, varnum ); 0x66030E
Id_fbk = DICE\_data_import(fname, varnum ); 0x66030D
Iq_fbk = DICE\_data_import(fname, varnum ); 0x66030B

Una funzione sotto main esegue il pull dei dati campionati ed esegue i calcoli:

1) ??Conversione della VBus in lsb della Vd Vq??
2) Calcolo del Ton
3) Calcolo della Vph[lsb]
4) Inserimento della Vph[lsb] quadratica nel filtro
5) Calcolo della Vph[lsb]
6) Calcolo del cos_phi
7) Calcolo della Vph in Volt
8) Calcolo della potenza apparente S [VA]
9) Calcolo della potenza attiva P         [W]
