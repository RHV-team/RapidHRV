import numpy as np
from rapidhrv import preprocess, analyze, visualize

# RapidHRV Tutorial

# Load in example data
data = np.load('Example_data.npy')

# Upsample, filter, and smooth data. Returns
procData = preprocess.preprocess(inputdata=data, samplingrate=20)

# Run analysis. Returns dictionary with analyzed time series (cleaned and uncleaned) and input parameter features.
analyzedData = analyze.extract_heart(inputdata=procData, resampledrate=1000)

# Create interactive visualization
fig = visualize.Visualize(inputdata=procData, inputframe=analyzedData)