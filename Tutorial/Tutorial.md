# RapidHRV Tutorial



Import packages and load data. Example data is a 5 minute segment of simulated PPG data downsampled to 20Hz and with added white gaussian noise (20dB)

~~~python
import numpy as np
from rapidhrv import preprocess, analyze, visualize

data = np.load('Example_data.npy')
~~~



Next, we will upsample, filter, and smooth the data using the preprocessing module

~~~python
procData = preprocess.preprocess(inputdata=data, samplingrate=20)
~~~



Here, you can see high-pass filtering has helped with some of the drift and also increased the temporal precision of peaks within the data 

![Example](https://github.com/peterakirk/RapidHRV/tree/viz_fix/Images/Example_data_overview.png)

![Example](https://github.com/peterakirk/RapidHRV/tree/viz_fix/Images/Example_data_peaks.png)



We will not submit this data to analysis, which outputs a dictionary containing the analyzed time series ('data') and parameter arguments used for analysis ('features').

~~~python
analyzedData = analyze.extract_heart(inputdata=procData, samplingrate=20)
~~~



Lastly, we can use the visualization module to have a check that RapidHRV is doing it's job.

~~~python
fig = analyze.extract_heart(inputdata=procData, inputframe=analyzedData)
~~~