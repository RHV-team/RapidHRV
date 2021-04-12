import numpy as np  # Arrays
from scipy.signal import butter, filtfilt, savgol_filter  # Signal processing
from scipy.interpolate import splrep, splev


# Define highpass filter
def _butter_highpass(cutoff, fs, order):
    nyq = 0.5 * fs
    cutoff = cutoff / nyq
    b, a = butter(N=order, Wn=cutoff, btype='highpass', output='ba')
    return b, a


# Apply butterworth filter
def _butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = _butter_highpass(cutoff=cutoff, fs=fs, order=order)
    y = filtfilt(b=b, a=a, x=data)
    return y


# Define lowpass filters
def _butter_lowpass(cutoff, fs, order):
    nyq = 0.5 * fs
    cutoff = cutoff / nyq
    b, a = butter(N=order, Wn=cutoff, btype='lowpass', output='ba')
    return b, a


# Apply butterworth filter
def _butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = _butter_lowpass(cutoff=cutoff, fs=fs, order=order)
    y = filtfilt(b=b, a=a, x=data)
    return y


def preprocess(inputdata, samplingrate, resample=1000, highpass=0.5, lowpass=None, polynomial=3, smooth=100):
    """Function to high pass filter and smooth cardiac data

    Parameters:
    inputdata (list): cardiac data to be preprocessed
    samplingrate (int): sampling rate in Hz
    resample(int): specify frequency in Hz. Uses cubic spline interpolation for resampling. Input 0 if not wanted.
    Optional (if samplingrate < resample, default=1000; else default=0)
    highpass (float/int): Optional (default=0.5)
    lowpass (float/int): Optional (default=None)
    polynomial(int): order of polynomial for savitzky-golay smoothing. Optional (default=3)
    smooth(int): window in ms for for savitzky-golay smoothing. Input None if not wanted. Optional (default=100)

    Returns:
    list:smoothed_data

   """

    if np.sum(np.isnan(inputdata)):
        raise ValueError(f'inputdata contains nan. preprocess requires no nans.')
    else:
        output = inputdata

    # First: upsample if specified
    if samplingrate < resample:
        if not resample % samplingrate == 0:
            raise ValueError(f'resample resolution (default=1000,used={resample}) must be divisible by original '
                             f'sampling rate ({samplingrate})')
        expansion = int(resample / samplingrate)
        samples = list(range(0, len(inputdata) * expansion, expansion))  # pretend samples are further apart in time
        tck = splrep(samples, inputdata, s=0, k=3)
        xnew = list(range(0, len(inputdata) * expansion))
        output = splev(xnew, tck, der=0)

    else:
        resample = samplingrate  # If no upsampling applied, redefine resample as original Hz for filtering

    # Second: highpass filter data
    if highpass:
        output = _butter_highpass_filter(data=output, cutoff=highpass, fs=resample)

    # Third: lowpass filter data (IF USING)
    if lowpass:
        output = _butter_lowpass_filter(data=output, cutoff=lowpass, fs=resample)

    # Smoothing with Savitsky-Golay filter
    if smooth:
        if smooth > 0:
            smoothing_window = int(np.round(samplingrate / (samplingrate / smooth)))
            if (smoothing_window % 2) == 0:  # If smoothing window is even (Sav-Gov requires odd)
                smoothing_window = smoothing_window + 1
            output = savgol_filter(output, window_length=smoothing_window, polyorder=polynomial)

    return output
