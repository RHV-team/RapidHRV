---
title: 'RapidHRV: An Open-Source Toolbox for Extracting Heart Rate and Heart Rate Variability'
tags:
  - Python
  - Psychophysiology
  - Heart rate variability
authors:
  - name: Peter A. Kirk
    orcid: 0000-0003-0786-3039
    affiliation: "1, 2"
  - name: Sarah N. Garfinkel
    orcid: 0000-0002-5961-1012
    affiliation: 1
  - name: Oliver J. Robinson
    orcid: 0000-0002-3100-1132
    affiliation: "1, 3"
affiliations:
 - name: Institute of Cognitive Neuroscience, University College London
   index: 1
 - name: Experimental Psychology, University College London
   index: 2
 - name: Clinical, Educational and Health Psychology, University College London
   index: 3
date: 29 April 2021
bibliography: paper.bib
---

# Summary

`RapidHRV` is a Python package ([PyPi](https://pypi.org/project/rapidhrv/)) dedicated to the
preprocessing, analysis, and visualization of time-domain heart rate (HR) and heart rate variability (HRV). Each of 
these modules can be executed with one function and includes automated cleaning. Validation across datasets showed 
good-to-excellent recovery of heart rate and heart rate variability, though estimates in photoplethysmography were less
stable under higher movement.

# Statement of need

Evidence has outlined a link between HR, HRV, and health-related risks 
[@Hillebrand:2013; @Jandackova:2016]. There is now an influx of research looking into whether these 
measures can be derived in naturalistic settings using e.g. wrist-worn photoplethysmography [@Georgiou:2018; @Mulcahy:2019].
A key issue that arises in these settings however is the low signal to noise ratio 
[@Caizzone:2017], leading to highly noisy points estimates. Whilst some packages are available for the analysis 
of HR/HRV, these are typically modality-specific, and not targeted at wrist-worn measures [@Legrand:2021]. 
Modality-general packages that do exist require considerable scripting if users want to adapt functions to noisy, 
wrist-worn measures [@van_Gent:2019]. Consequently, we set out to develop a simple yet flexible toolbox for the
extraction of time-domain HR/HRV measures with automated artifact rejection applicable across recording modalities.

# Overview and Examples

Below we provide an overview of `RapidHRV`'s preprocessing, analysis (figure 1), and visualization. Each of the three 
modules only requires one function to run, for which we have embedded examples at the end of the relevant sections below.

![Overview of `RapidHRV` pipeline. Across an entire block, the pipeline initially processes data with high-pass 
filtering, upsampling, and smoothing. `RapidHRV` then applies a sliding window across the entire block. Within each 
window, the data are scaled. HR (beats per minute, BPM) and HRV (root mean squared of successive
differences, RMSSD, + standard deviation of intervals) are calculated for each window, and data is submitted to outlier 
rejection. `RapidHRV` produces both a cleaned and uncleaned time series of HR/HRV.
](https://github.com/peterakirk/RapidHRV/blob/main/Images/Pipeline_overview.jpg?raw=true)

In preprocessing, data is: 1) upsampled (cubic spline interpolation; default = 1kHz) to increase precision of peak 
detection; 2) high-pass filtered (0.5Hz) to mitigate long-term drifts; 3) smoothed (savitzky-golay filter) to reduce 
spiking; and 4) normalized between 0-100 (performed within analysis). Preprocessing example:

```python
from rapidhrv import preprocess

processedData = preprocess.preprocess(inputData, Hz)
```

Within analysis, peak detection is run on every window (default width = 10s) using `SciPy`'s 
‘find_peaks’ [@Virtanen:2020]. These windows are then submitted to outlier rejection (figure 2). By default, 
`RapidHRV` returns the cleaned and the uncleaned time series in a pandas DataFrame [@McKinney:2012]. Given that not
all users may be comfortable adjusting parameters, `RapidHRV` additionally contains 
semantically-labelled arguments ('liberal', 'moderate' [default], and 'conservative') as inputs for outlier constraints
(see below for details). Analysis example:

```python
from rapidhrv import analyze

analyzedData = analyze.extract_heart(processedData, resampledRate)
```

![Outlier rejection methods. Firstly, the windows is screening for a sufficient number of peaks to derive 
metrics before HR/HRV. Statistical constraints (Median Absolute Deviation; MAD) are then applied to peak properties. 
Lastly, `RapidHRV` ensures an adequate duration from first to last peak.
](https://github.com/peterakirk/RapidHRV/blob/main/Images/Outlier_flowchart.jpg?raw=true)

To allow for selective inspection, we have implemented optional interactive visualizations via `matplotlib` 
[@Hunter:2007]. This plots the analyzed HR/HRV time course; the user can then
select and view specific data points to see the window of extraction (figure 3). Visualization example:

```python
from rapidhrv import visualize

fig = visualize.Visualize(processedData, analyzedData)
```

![Interactive visualization. The user is presented with a raw and cleaned time series of BPM (background, top two red 
plots) and RMSSD (background, bottom two purple plots). Users can click on specific time points to view extraction 
windows (top right; foreground). Extraction windows display BPM/RMSSD, as well as properties of peak detection (peak 
position \[marked with an X\], baseline \[black dashed line\], height/prominence thresholds for outlier rejection 
\[grey/purple dashed lines\]).
](https://github.com/peterakirk/RapidHRV/blob/main/Images/Time_series_with_click.png?raw=true)

# Validation

To validate the above pipeline we subjected it to a series of tests across 5 datasets varying in modality 
(electrocardiography, pulse oximetry, and photoplethysmography; real and simulated). We briefly outline key findings 
below. For full reporting of all tests, see our [preprint](https://psyarxiv.com/3ewgz/) [@Kirk:2021]. 

`RapidHRV` was able to accurately recover HR/HRV across sampling frequencies and in relatively noisy 
photoplethysmography simulations [@Tang:2020]. Cleaning provided improvements in noisier simulations (figure 4).

![Parameter recovery of simulated PPG data as a function of heart rate variability. Y axes reflect the true 
RMSSD in the data, whilst the X axes reflect `RapidHRV`’s estimation. For 
readability, data is only plotted in a key range of performance, 10dB to 40dB of signal to noise ratio). 
](https://github.com/peterakirk/RapidHRV/blob/main/Images/HRV_plot.png?raw=true)

Benchmarking in pulse oximetry data demonstrated good-to-excellent agreement (Intraclass Correlation; ICC) between 
`RapidHRV` and previous estimates [@de_Groot:2020] implemented with `LabChart` (ADInstruments, Sydney, Australia; figure
5).

![Agreement between RapidHRV and a previous analysis [@de_Groot:2020] in 
a pulse oximetry dataset (N=39).](https://github.com/peterakirk/RapidHRV/blob/main/Images/Benchmarking_plot.png?raw=true)

During low motion activities, RapidHRV PPG-based estimates converged with previously reported, simultaneous ECG-based 
estimates (BPM ICC > .90; .57 < RMSSD ICC < .82) derived from an automated analysis with visual inspection 
[@Reiss:2019]. Under high motion conditions, estimates showed poor agreement (ICC < .32), except during cycling (BPM 
ICC = .75).

![Agreement between PPG RapidHRV estimates and a visually inspected ECG analysis across different activities.
](https://github.com/peterakirk/RapidHRV/blob/main/Images/Wrist_PPG_benchmarking.png?raw=true)

# Acknowledgements

Massive thanks to Alex Davidson Bryan for helping publish the package and Kaarina Aho for statistical consultation. 
Appreciation goes to other open-source analysis software, namely `Systole` [@Legrand:2021] and `HeartPy` 
[@van_Gent:2019], which helped inspire the development of `RapidHRV`. Finally, thank you to Russell Kirk for 
advice on deriving accelerometer motion estimates. This work was supported by the Leverhulme Trust as part of the 
Doctoral Training Program for the Ecological Study of the Brain (DS-2017-026).

# References