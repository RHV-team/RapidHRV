![Logo](./Images/Logo.png?raw=true)


RapidHRV is a Python library for preprocessing, analyzing, and visualizing cardiac data (validated on ECG, Pulse Oximetry, and PPG).

## Installation

```bash
pip install rapidhrv
```

## Usage
RapidHRV comes with three modules, each of which requires one function to run. For a step-by-step tutorial, see 
[Tutorial.md](./Tutorial/Tutorial.md).

```python
from rapidhrv import preprocess, analyze, visualize

procData = preprocess.preprocess(inputdata=mydata, samplingrate=250)  # returns upsampled, high-pass filtered, smoothed data

analyzedData = analyze.extract_heart(inputdata=procData,resampledrate=1000)  # returns dictionary with analyzed data

fig = visualize.Visualize(inputdata=procData, inputframe=analyzedData)  # returns interactive matplotlib object, displaying BPM and RMSSD time series
```

## Visualization Bug

At present (V 0.0.6), the visualization module has been verified to work in Pycharm on an Ubuntu 20.04 OS. Some users 
have noted issues with interactive plotting in other IDEs/operating systems. We are currently working on a fix.

## License
MIT License
