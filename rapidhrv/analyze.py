import numpy as np  # Arrays
import pandas as pd  # Dataframes
from scipy.stats import median_abs_deviation  # MAD tests
from scipy.signal import find_peaks
from sklearn.cluster import KMeans


# Function to scale data
def _normalize_data(data):
    return (data - np.min(data)) * 100 / (np.max(data) - np.min(data))


# Derive RMSSD
def _get_rmssd(inputpeaks, samplingrate, minpeaks):
    if len(inputpeaks) > minpeaks:
        IBI = np.array([x - inputpeaks[i - 1] for i, x in enumerate(inputpeaks)][1:])  # Interbeat Intervals
        IBIms = IBI * 1000 / samplingrate  # Convert to ms (1000)
        SD = np.diff(IBIms)  # Successive differences in IBI
        SSD = np.square(SD)  # Square of successive differences
        MSSD = np.mean(SSD)  # Mean square of successive differences
        RMSSD = np.sqrt(MSSD)  # Root mean square of successive differences
        return RMSSD
    else:
        return np.nan


# Derive SDNN
def _get_sdnn(inputpeaks, samplingrate, minpeaks):
    if len(inputpeaks) > minpeaks:
        IBI = np.array([x - inputpeaks[i - 1] for i, x in enumerate(inputpeaks)][1:])  # NN Intervals
        IBIms = IBI * 1000 / samplingrate  # Convert to ms (1000)
        SDNN = np.std(IBIms)  # Standard deviation of NN intervals
        return SDNN
    else:
        return np.nan


# Derive BPM
def _get_bpm(inputpeaks, samplingrate, minpeaks):
    if len(inputpeaks) > minpeaks:
        actWindow = ((inputpeaks[-1] - inputpeaks[0]) / samplingrate)
        BPM = ((len(inputpeaks) - 1) * 60) / actWindow
        return BPM
    else:
        return np.nan


# Outlier detection
def _outlier_detect(inputdata, inputpeaks, properties, minpeaks, minwindow, samplingrate, mad, ibimad, bpmrange,
                    rmssdrange):

    if len(inputpeaks) < minpeaks:
        return True, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
    else:
        # Get BPM/RMSSD
        bpm = _get_bpm(inputpeaks=inputpeaks, samplingrate=samplingrate, minpeaks=minpeaks)
        rmssd = _get_rmssd(inputpeaks=inputpeaks, samplingrate=samplingrate, minpeaks=minpeaks)

        # Gather data
        baseheight = inputdata[inputpeaks] - properties['prominences']  # Baseline
        prominences = properties['prominences'] - np.mean(properties['prominences'])  # Mean center prominences
        heights = properties['peak_heights'] - np.mean(properties['peak_heights'])  # Mean center heights
        IBI = np.array([x - inputpeaks[i - 1] for i, x in enumerate(inputpeaks)][1:])  # Interbeat intervals
        IBI = IBI - np.mean(IBI)  # Mean-center

        # Check window length
        actwindowwidth = ((inputpeaks[-1] - inputpeaks[0]) / samplingrate)

        # Detect prominence outliers
        promMADUnits = median_abs_deviation(prominences)  # Calculate MAD units
        promOutliers = [np.greater(prominences, mad * promMADUnits) |
                        np.less(prominences, -mad * promMADUnits)]  # Detect outliers

        # Detect height outliers
        heightMADUnits = median_abs_deviation(heights)  # Calculate MAD units
        heightOutliers = [np.greater(heights, mad * heightMADUnits) |
                          np.less(heights, -mad * heightMADUnits)]  # Detect  outliers

        # Detect successive difference outliers
        IBIMADUnits = median_abs_deviation(IBI)  # Calculate MAD units
        IBIOutliers = [np.greater(IBI, ibimad * IBIMADUnits) |
                       np.less(IBI, -ibimad * IBIMADUnits)]  # Detect  outliers

        # Height thresholds
        heightThresholds = [(-mad * heightMADUnits) + np.mean(properties['peak_heights']),
                            (mad * heightMADUnits) + np.mean(properties['peak_heights'])]

        # Prominence thresholds
        PromLowThreshold = baseheight + np.mean(properties['prominences']) - (mad * promMADUnits)
        PromHighThreshold = baseheight + np.mean(properties['prominences']) + (mad * promMADUnits)
        prom_Thresholds = [PromLowThreshold, PromHighThreshold]

        OutlierCheck = np.any(promOutliers) | np.any(heightOutliers) | np.any(IBIOutliers) | \
                       (actwindowwidth < minwindow) | (bpm < bpmrange[0]) | (bpm > bpmrange[1]) | \
                       (rmssd < rmssdrange[0]) | (rmssd > rmssdrange[1])

        return OutlierCheck, prom_Thresholds, heightThresholds, promOutliers, heightOutliers, IBIOutliers, baseheight


# Function to run peak detection on a window.
def _get_peaks(inputdata, distance=200, prominence=50, k=1):
    peaks, properties = find_peaks(inputdata, distance=distance, height=0, prominence=prominence, width=0)

    if (len(peaks) >= 3) & (k > 1):
        clusteringdata = np.empty([len(peaks), 3])  # Generate feature matrix
        clusteringdata[:] = np.NaN
        clusteringdata[:, 0] = properties['widths'][:]
        clusteringdata[:, 1] = properties['peak_heights'][:]
        clusteringdata[:, 2] = properties['prominences'][:]

        kmeans = KMeans(n_clusters=k).fit(clusteringdata)  # Cluster data in P, R, and T waves
        widthcen = kmeans.cluster_centers_[:, 0]  # Get centroid of width feature

        # Check if width centroids are close (within 5). If so, use other parameter
        if np.abs(np.diff(np.sort(widthcen)[0:2])[0]) < 5:  # If less than 5, use height instead
            widthidx = np.argsort(widthcen)[0:2]  # Get indices of two lowest widths
            heightcen = kmeans.cluster_centers_[:, 2]  # Prominence centroids
            maxheight = np.max(heightcen[widthidx])  # Maximum prominence centroid for two lowest widths
            peakcluster = np.where(heightcen == maxheight)[0][0]  # Which label has higher prominence
        else:
            peakcluster = np.where(widthcen == np.min(widthcen))[0][0]  # Which label has lower width

        correctpeaks = kmeans.labels_ == peakcluster
        peaks = peaks[correctpeaks]  # Replace original peak/property values
        for dictkey in properties.keys():
            properties[dictkey] = properties[dictkey][correctpeaks]

    if len(peaks) > 3:
        baseheight = inputdata[peaks] - properties['prominences']  # Baseline
        properties['prominences'][0] = properties['peak_heights'][0] - baseheight[1]
        properties['prominences'][-1] = properties['peak_heights'][-1] - baseheight[-2]
        # The nature of random sampling windows means the baseline value may be off the mark. As such, the baseline for
        # the first peak is estimated using neighboring peak. This requires at least 3 peaks.

    return peaks, properties


def _moving_window(inputdata, windowwidth, windowmovement, samplingrate, numpeaksneeded, mad, ibimad, minamplitude,
                   minwindow, bpmrange, rmssdrange, mindistance, clusters):
    dataFrameCols = ['Time', 'BPM', 'CleanedBPM', 'RMSSD', 'CleanedRMSSD', 'SDNN', 'CleanedSDNN']
    rapiddata = pd.DataFrame(columns=dataFrameCols)

    for section in range(0, len(inputdata) - int(windowwidth * samplingrate) + 1, int(windowmovement * samplingrate)):
        exptime = section / samplingrate  # Note time

        # RAPID HRV PIPELINE
        segment = inputdata[section:section + (
                windowwidth * samplingrate)]  # Take initial window
        normed_data = _normalize_data(data=segment)  # Scale so min = 0, max = 100
        peaks, properties = _get_peaks(inputdata=normed_data, distance=mindistance, prominence=minamplitude, k=clusters)

        BPM = _get_bpm(inputpeaks=peaks, samplingrate=samplingrate, minpeaks=numpeaksneeded)  # HR
        RMSSD = _get_rmssd(inputpeaks=peaks, samplingrate=samplingrate, minpeaks=numpeaksneeded)  # HRV
        SDNN = _get_sdnn(inputpeaks=peaks, samplingrate=samplingrate, minpeaks=numpeaksneeded)

        Outliers, _, _, _, _, _, _ = \
            _outlier_detect(inputdata=normed_data, inputpeaks=peaks, properties=properties, minpeaks=numpeaksneeded,
                            minwindow=minwindow, samplingrate=samplingrate, mad=mad, ibimad=ibimad, bpmrange=bpmrange,
                            rmssdrange=rmssdrange)

        if Outliers:
            cleanedBPM = np.nan
            cleanedRMSSD = np.nan
            cleanedSDNN = np.nan
        else:
            cleanedBPM = BPM
            cleanedRMSSD = RMSSD
            cleanedSDNN = SDNN

        rapiddata = rapiddata.append(
            pd.DataFrame(data=[[exptime, BPM, cleanedBPM, RMSSD, cleanedRMSSD, SDNN, cleanedSDNN]],
                         columns=dataFrameCols))

    return rapiddata, clusters


# Go over with rolling window
def extract_heart(inputdata, resampledrate, ecgclustering=False, windowwidth=10, windowmovement=None, minamplitude=50,
                  outliermethod='moderate', mad=None, ibimad=None, bpmrange=None, rmssdrange=None, numpeaksneeded=None,
                  minwindow=None, mindistance=None):
    """Function to extract heart rate (BPM) and variability (RMSSD) from heart data

    Parameters: inputdata (list): preprocessed cardiac data to be analysed.
    resampledrate (int): sampling rate in Hz. If data has been upsampled from preprocessing, make sure this. If no
    upsampling has been performed at preprocessing, use original sampling rate.
    ecgclustering (bool): whether to use k-means clustering to discern P, R, and T waves in the ECG signal. This
    overrides minamplitude and mindistance, setting them to 10 and 1 respectively. For clean ECG data that contains
    atypical morphologies (e.g. T wave amplitude > R wave amplitude), this may be useful. Optional (default=False)
    windowwidth (int): width of sliding window (in seconds) for which measures are extracted. Optional (default=10)
    windowmovement (int): how much the sliding window is shifted by (in seconds). Optional (default=windowwidth)
    minamplitude (int): the minimum amplitude before a peak is detected as a heart beat. Lower values = greater
    sensitivity, though at the risk of false detections. For PPG data, it is recommended to lower this to ~30.
    Optional (default=50)
    outliermethod (string): this will accept the arguments 'none','liberal','moderate','conservative' to determine
    the stringency of outlier rejection. 'liberal' will likely result in the least amount of cleaning, but risks
    introducing noise. 'conservative' will likely result in a larger amount of excluded data, but is less likely to
    introduce noise. Optional (default 'moderate')
    mad (int): the threshold (in median absolute deviation units) to detect whether peak height and prominences may be
    noise/outliers. Optional (if outliermethod == 'moderate': default=5)
    ibimad (int): the threshold (in median absolute deviation units) for detecting outliers based on peak intervals.
    Optional (if outliermethod == 'moderate': default=5)
    bpmrange (list): sets the lower and upper limits for deciding a window is an outlier based on BPM. Optional
    (if oulitermethod == 'moderate', default = [30, 190])
    rmssdrange (list): sets the lower and upper limits for deciding a window is an outlier based on RMSSD. Optional
    (if outliermethod == 'moderate', default = [5, 262])
    numpeaksneeded (int): the number of peaks needed for successful BPM/RMSSD extraction. Applies to both cleaned and
    uncleaned outputs. All input floored at 3. Optional (default = round((windowwidth / 5) + 2))
    minwindow (int): the minimum time (s) from first to last peak before a window is classified as an outlier. Optional
    (default=windowwidth/2)
    mindistance (int): minimum distance (in samples) required between peaks. Optional
    (default = round(samplingrate / 4) ≈ 250ms)

    Returns:
    dictionary:output. ['data'] is Dataframe containing experiment time (starting from 0), Uncleaned BPM, Cleaned BPM,
    Uncleaned RMSSD, and Cleaned RMSSD. ['features'] contains parameters from extract_heart.

   """

    if outliermethod == 'liberal':
        if bpmrange is None:
            bpmrange = [20, 200]
        if rmssdrange is None:
            rmssdrange = [0, 300]
        if mad is None:
            mad = 7
        if ibimad is None:
            ibimad = 7
    elif outliermethod == 'moderate':
        if bpmrange is None:
            bpmrange = [30, 190]
        if rmssdrange is None:
            rmssdrange = [5, 262]
        if mad is None:
            mad = 5
        if ibimad is None:
            ibimad = 5
    elif outliermethod == 'conservative':
        if bpmrange is None:
            bpmrange = [40, 180]
        if rmssdrange is None:
            rmssdrange = [10, 200]
        if mad is None:
            mad = 4  # Note: has been changed to 4
        if ibimad is None:
            ibimad = 4
    else:
        if (bpmrange is None) | (rmssdrange is None) | (mad is None) | (ibimad is None):
            raise ValueError('extract_heart requires either outliermethod or outlier-specific arguments (bpmrange,'
                             'rmssdrange, madrange, and ibimadrange). Is the outliermethod argument spelt correctly?')

    if windowmovement is None:
        windowmovement = windowwidth

    if minwindow is None:
        minwindow = windowwidth / 2

    if numpeaksneeded is None or numpeaksneeded < 3:
        if int(np.round((windowwidth / 5) + 2)) < 3:
            numpeaksneeded = 3
        else:
            numpeaksneeded = int(np.round((windowwidth / 5) + 2))

    if mindistance is None:
        mindistance = round(resampledrate / 4)
    else:
        mindistance = 500

    if ecgclustering:
        minamplitude = 5
        mindistance = 1
        clusters = 3
    else:
        clusters = 1

    data, k = _moving_window(inputdata, windowwidth, windowmovement, resampledrate, numpeaksneeded, mad, ibimad,
                             minamplitude, minwindow, bpmrange, rmssdrange, mindistance, clusters)

    output = {
        'data': pd.DataFrame(columns=['Time', 'BPM', 'CleanedBPM', 'RMSSD', 'CleanedRMSSD', 'SDNN', 'CleanedSDNN']),
        'features': {'samplingrate': resampledrate, 'windowwidth': windowwidth, 'windowmovement': windowmovement,
                     'numpeaksneeded': numpeaksneeded, 'mad': mad, 'ibimad': ibimad, 'minamplitude': minamplitude,
                     'minwindow': minwindow, 'bpmrange': bpmrange, 'rmssdrange': rmssdrange, 'mindistance': mindistance,
                     'ecgclustering': clusters}}

    output['data'] = output['data'].append(data, ignore_index=True)

    return output
