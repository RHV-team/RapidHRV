![Logo](https://github.com/peterakirk/RapidHRV/blob/main/Images/Logo.png?raw=true)


RapidHRV is a Python pipeline for the analysis and visualization of cardiac data (validated on ECG, Pulse Oximetry, and 
PPG).

Please provide credit where appropriate:

Kirk, P. A., Garfinkel, S., & Robinson, O. J. (2021). RapidHRV: An open-source toolbox for extracting heart rate and 
heart rate variability. PsyArXiv. https://doi.org/10.31234/osf.io/3ewgz.


## Installation

```bash
pip install rapidhrv
```

## Usage
RapidHRV comes with three modules, each of which requires one function to run. For a step-by-step tutorial, see 
[Tutorial.md](https://github.com/peterakirk/RapidHRV/blob/main/Tutorial/Tutorial.md).

```python
from rapidhrv import preprocess, analyze, visualize

procData = preprocess.preprocess(inputdata=mydata, samplingrate=250)  # returns upsampled, high-pass filtered, smoothed data

analyzedData = analyze.extract_heart(inputdata=procData,resampledrate=1000)  # returns dictionary with analyzed data

fig = visualize.Visualize(inputdata=procData, inputframe=analyzedData)  # returns interactive matplotlib object, displaying BPM and RMSSD time series
```

Based on our validation paper (https://psyarxiv.com/3ewgz/), we make the following modality-specific suggestions as 
starting points for function arguments.

![Suggestions](https://github.com/peterakirk/RapidHRV/blob/main/Images/Modality_suggestions.png?raw=true)

## Interactive Visualizations

Some users have noted IDE-specific issues with interactive plotting which we believe is related to the way matplotlib 
employs user interface backends. At present (0.1.4), the visualization module has been verified to work in Pycharm, 
Spyder, Jupyter Notebook, Visual Studio Code, and the ordinary Python shell on an Ubuntu 20.04 OS, though some of these
require a workaround (see below). It will not work on IDLE 
([details](https://matplotlib.org/3.1.0/tutorials/introductory/usage)).

**Spyder** users will need to change the backend to automatic via Tools > preferences > IPython console > Graphics > 
Graphics backend > Backend: Automatic. Then close/re-open Spyder. Instead of plotting figures in the console, figures 
will now open in a new window.

**Jupyter Notebook/Visual Studio Code** users will need to specify the matplotlib backend at the very beginning of the script. For a 
full list of acceptable arguments, see [here](https://matplotlib.org/2.0.2/faq/usage_faq.html#what-is-a-backend). 
Example:

```python
import matplotlib
matplotlib.use('tkagg')
import numpy as np
from rapidhrv import preprocess, analyze, visualize
```

## License
MIT License
