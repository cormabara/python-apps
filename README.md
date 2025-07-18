# Python MB applications

This is a basic package of simple applications 

## Fourier

The fourier script take 3 parameters:

- Name (with path) of the .osc.cvs file, if name is missing a dialog opens
- total number of channels inside the oscillo
- Number of the channel to make transfiormation (1-8)

In output is a plot with the fft transform of the channel selected and  also a 

```
<name file>_output.osc.csv
```

 file with 3 columns:

- sample number
- frequency
- fft value (mDb)
