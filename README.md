# RapidHRV

RapidHRV is a Python library for preprocessing, analyzing, and visualizing cardiac data (ECG, Pulse Oximetry, and PPG)

## Installation



```bash

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

## Contributing


## License
MIT License

Copyright (c) 2021 Peter A. Kirk, Sarah N. Garfinkel, & Oliver J. Robinson.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
