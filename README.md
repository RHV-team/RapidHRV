![Logo](./Images/Logo.png?raw=true)


RapidHRV is a Python library for preprocessing, analyzing, and visualizing cardiac data (validated on ECG, Pulse Oximetry, and PPG).

## Installation

```bash
pip install rapidhrv
```

## Usage

```python
from rapidhrv import preprocess, analyze, visualize

processedData = preprocess.preprocess(inputdata=mydata, samplingrate=250)  # returns upsampled, high-pass filtered, smoothed data

analyzedData = analyze.extract_heart(inputdata=processedData,resampledrate=1000)  # returns dictionary with analyzed data

fig = visualize.Visualize(inputdata=processedData, inputframe=analyzedData)  # returns interactive matplotlib object, displaying BPM and RMSSD time series

```

## Visualization Bug

At present (V 0.0.6), the visualization module has been verified to work in Pycharm. Some users have noted issues with interactive 
plotting in other IDEs. We are currently working on this.

## License
MIT License
