# RapidHRV

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

fig = visualize.visualize(inputdata=processedData, inputframe=analyzedData)  # returns interactive matplotlib object, displaying time series BPM and RMSSD time series

```

## License
MIT License
