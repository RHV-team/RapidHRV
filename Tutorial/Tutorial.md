# RapidHRV Tutorial



Import packages and load data. Example data is a 5 minute segment of simulated PPG data downsampled to 20Hz and with added white gaussian noise (20dB)

~~~python
```python
import numpy as np
from rapidhrv import preprocess, analyze, visualize

data = np.load('Example_data.npy')
```
~~~



Next, we will upsample, filter, and smooth the data using the preprocessing module

```python
​```python
procData = preprocess.preprocess(inputdata=data, samplingrate=20)
​```
```



Here, you can see high-pass filtering has helped with some of the drift and also increased the temporal precision of peaks within the data 

![Logo](https://github.com/peterakirk/RapidHRV/blob/main/Tutorial/Example_data_overview.png?raw=true)

![Logo](https://github.com/peterakirk/RapidHRV/blob/main/Tutorial/Example_data_peaks.png?raw=true)



We will not submit this data to analysis, which outputs a dictionary containing the analyzed time series ('data') and parameter arguments used for analysis ('features').

```python
​```python
analyzedData = analyze.extract_heart(inputdata=procData, samplingrate=20)
​```
```

Lastly, we can use the visualization module to have a check that RapidHRV is doing it's job.