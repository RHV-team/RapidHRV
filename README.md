# RapidHRV

RapidHRV is a Python library for preprocessing, analyzing, and visualizing cardiac data (ECG, Pulse Oximetry, and PPG)

## Installation



```bash

```

## Usage

```python
import rapidhrv.preprocess
import rapidhrv

rapidhrv.preprocess.preprocess(inputdata=mydata, samplingrate=1000)  # returns high-pass filtered, smoothed data
rapidhrv.analyze.extract_heart(inputdata=mypreprocessed_data,
                               samplingrate=1000)  # returns uncleaned/cleaned BPM/RMSSD dataframe and a list of input parameters ("features")
rapidhrv.visualize.visualize(inputdata=mypreprocessed_data, inputframe=myheartdata,
                             features=myfeatures)  # returns interactive matplotlib object, displaying time series BPM and RMSSD time series

```

## Contributing


## License
