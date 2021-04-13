# RapidHRV

RapidHRV is a Python library for preprocessing, analyzing, and visualizing cardiac data (validated on ECG, Pulse Oximetry, and PPG)

## Installation

```bash
pip install rapidhrv
```

## Usage

```python
import rapidhrv.preprocess
import rapidhrv

processedData = rapidhrv.preprocess.preprocess(inputdata=mydata, samplingrate=250)  # returns upsampled, high-pass filtered, smoothed data

rapidhrv.analyze.extract_heart(inputdata=processedData,resampledrate=1000)  # returns dictionary with analyzed data

rapidhrv.visualize.visualize(inputdata=mypreprocessed_data, inputframe=myheartdata,
                             features=myfeatures)  # returns interactive matplotlib object, displaying time series BPM and RMSSD time series

```

## License
MIT License
