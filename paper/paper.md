---
title: 'RapidHRV: An Open-Source Toolbox for Extracting Heart Rate and Heart Rate Variability'
tags:
  - Python
  - Psychophysiology
  - Heart rate
  - Heart rate variability
  - ECG
  - Pulse Oximetry
  - PPG
authors:
  - name: Peter A. Kirk^[Corresponding author. Email: p.kirk@ucl.ac.uk]
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

`RapidHRV` is a Python package dedicated to the preprocessing, analysis, and visualization of time-domain heart rate and 
heart rate variability. Each of these modules can be executed with one line of code and includes automated cleaning. 
Validation in real and simulated datasets generally showed good-to-excellent recovery of heart rate and heart rate 
variability, though estimates in photoplethysmography were less stable under higher movement settings.

# Statement of need

Evidence has outlined a link between heart rate (HR), heart rate variability (HRV), and health-related risks 
`[@Hillebrand:2013; @Jandackova:2016]`. There is now an influx of research looking into whether these 
measures can be derived in naturalistic settings (e.g. wrist-worn photoplethysmography Georgiou et al., 2018; Mulcahy 
et al., 2019). A key issue that arises in these settings however is the low signal to noise ratio 
`[@Caizzone:2017]`, leading to highly noisy points estimates. Whilst some packages are available for the analysis 
of HR/HRV, these are typically modality-specific, and not targeted at wrist-worn measures (e.g. systole for pulse 
oximetry, `@Legrand:2021`). Modality-general packages that do exist require considerable scripting if users want 
to adapt functions to noisy, wrist-worn measures (‘Analysing_Smartwatch_Data’ in HeartPy, `@van Gent:2019`). 
Consequently, we set out to develop a simple yet flexible toolbox for the extraction of time-domain HR/HRV measures with
automated artifact rejection applicable across recording modalities.

# Overview and Examples

Below we provide an overview of `RapidHRV`'s preprocessing, analysis (figure 1), and visualization. Each of the three 
modules only requires one function to run, for which we have embedded examples at the end of the relevant sections below.

![Figure 1. Overview of `RapidHRV` pipeline. Across an entire block, the pipeline initially processes data with high-pass 
filtering, upsampling, and smoothing. `RapidHRV` then applies a sliding window across the entire block. Within each 
window, the data are scaled. Heart rate (beats per minute) and heart rate variability (root mean squared of successive
differences + standard deviation of intervals) are calculated for each window, and data is submitted to outlier 
rejection. `RapidHRV` produces both a cleaned and uncleaned time series of heart rate and heart rate variability.
](https://github.com/peterakirk/RapidHRV/blob/main/Images/Pipeline_overview.jpg?raw=true)

In preprocessing, data is: 1) upsampled with cubic spline interpolation (3rd order polynomial; default = 1kHz) to 
increase temporal accuracy of peak detection; 2) high-pass filtered (0.5Hz) to mitigate potential long-term drifts in 
the signal; 3) smoothed (3rd order savitzky-golay; default = 100ms) reduce signal spiking whilst retaining temporal 
precision; and 4) Normalization between 0-100 (this is performed at the level of a sliding window during the analysis 
stage ‘analyze’ module). Preprocessing example:

```python
from rapidhrv import preprocess

processedData = preprocess.preprocess(inputData, samplingRate)
```

Following preprocessing, the pipeline runs peak detection on every window (default width = 10s; built on top of SciPy 
‘find_peaks’, `[@Virtanen:2020]`). These windows are then submitted to outlier rejection (figure 2). By default, 
`RapidHRV` returns both the cleaned and the uncleaned time series in a pandas DataFrame (`@McKinney:2012`; e.g. 
analyzedData['data']). Given that not all users may be entirely comfortable manually adjusting argument parameters, 
`RapidHRV` additionally contains semantically-labelled arguments ('liberal', 'moderate' [default], and 'conservative') as 
inputs for outlier constraints (see below for details). Analysis example:

```python
from rapidhrv import analyze

analyzedData = analyze.extract_heart(inputData, resampledRate)
```

To allow for selected manual inspection, we have also implemented optional interactive visualizations via matplotlib 
`[@Hunter:2007]` which allow the user to plot the time course of heart rate and heart rate variability. The user can then
select and view specific data points to see the window of extraction (Figure 3). Visualization example:

```python
from rapidhrv import visualize

fig = visualize.Visualize(processedData, analyzedData)
```

![Figure 2. Interactive visualization. The user is presented with a raw and cleaned time series of BPM (background, top 
two red plots) and RMSSD (background, bottom two purple plots). Users can click on specific time points to view 
extraction windows (top right; foreground). Extraction windows display BPM/RMSSD, as well as properties of peak 
detection (peak position marked with an X, black dashed baseline, grey/purple dashed lines for height/prominence 
thresholds used in outlier rejection). 
](https://github.com/peterakirk/RapidHRV/blob/main/Images/HRV_plot.png?raw=true)

# Validation

To validate the above pipeline we subjected it to a series of tests across 5 datasets  (simulated and real) varying in 
modality (electrocardiography, pulse oximetry, and photoplethysmography; for full reporting of all tests, see 
https://psyarxiv.com/3ewgz/). In brief, `RapidHRV` was able to accurately recover heart rate and heart rate variability 
across sampling frequencies and in relatively noisy photoplethysmography simulations (`@Tang:2020`; figure 3). 
`RapidHRV` cleaning provided improvements in noisier simulations.

![Figure 3. Parameter recovery of simulated PPG data as a function of heart rate variability. Y axes reflect the true 
root mean square of successive differences (RMSSD) in the data, whilst the X axes reflect RapidHRV’s estimation. For 
readability, data is only plotted in a key range of performance, 10dB to 40dB of signal to noise ratio). 
](https://github.com/peterakirk/RapidHRV/blob/main/Images/Time_series_with_click.png?raw=true)

Benchmarking in pulse oximetry data demonstrated excellent agreement between `RapidHRV` and previous estimates 
(`@de Groot:2020`; implemented using LabChart, ADInstruments, Sydney, Australia) of BPM (Intraclass Correlations >
.99; figure 6). For heart rate variability, there was good agreement when using the cleaned time series (ICC = .88), 
but poor agreement when using the uncleaned time series (ICC = .46).

![Figure 4. Agreement between RapidHRV and a previous analysis (de Groot et al., 2020) of heart rate and variability in 
a pulse oximetry dataset (N=39).](https://github.com/peterakirk/RapidHRV/blob/main/Images/Benchmarking_plot.png?raw=true)

# Acknowledgements

Massive thanks to Alex Davidson Bryan for helping publish the package and Kaarina Aho for statistical consultation. 
Appreciation goes to other open-source analysis software, namely Systole `[Legrand:2021]` and HeartPy 
`[van Gent:2019]`, which helped inspire the development of `RapidHRV`. Finally, thank you to Russell Kirk for 
advice on deriving motion estimates.

# References