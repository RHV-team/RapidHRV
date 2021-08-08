import dataclasses
from typing import Union

import numpy as np
import numpy.typing
import pandas as pd
import scipy.signal

from .data import OutlierDetectionSettings


def normalize(segment: np.ndarray) -> np.ndarray:
    """Scale all input to be between 0 and 1."""
    min_ = np.min(segment)
    max_ = np.max(segment)
    return (segment - min_) / (max_ - min_)


def peak_detection(
    segment: np.ndarray, distance: int, prominance: int, k: int
) -> tuple[np.ndarray, dict]:
    """Returns the indexes of detected peaks and associated properties."""
    peaks, properties = scipy.signal.find_peaks(
        segment, distance=distance, prominance=prominance, height=0, width=0
    )
    print(properties)
    n_peaks = len(peaks)

    if len(peaks) >= 3 and k > 1:
        clustering_data = np.empty((len(peaks), 3))


def analyze(
    input_data: np.ndarray,
    sampling_rate: int,
    window_width: int = 10,
    window_overlap: int = 0,
    ecg_prt_clustering: bool = False,
    amplitude_threshold: int = 50,
    distance_threshold: int = 250,
    n_required_peaks: int = 3,
    outlier_detection: Union[str, OutlierDetectionSettings] = "moderate",
) -> pd.DataFrame:
    """Analyzes cardiac data.

    Extracts BPM, RMSSD and SDNN from `input_data`.

    Parameters
    ----------
    input_data : array_like
        Cardiac data to be analyzed.
    sampling_rate : int
        Sampling rate of `input_data` in hertz.
        If the signal was previously up-sampled use the new sampling rate, not the original.
    window_width : int, default: 10
        Width of the sliding window in seconds.
    window_overlap: int, default: 0
        Amount of overlap between windows in seconds.
        Accepts negative values, interpreted as space between windows.
    ecg_prt_clustering: bool, default: False
        Use k-means clustering to detect P, R and T waves in the data.
        Useful for atypical morphologies (e.g. T amplitude > R amplitude).
        If enabled, `amplitude_threshold` and `distance_threshold` will be ignored.
    amplitude_threshold: int, default: 50
        Minimum signal amplitude for a peak to be registered.
        For PPG data, the recommended value is 30.
    distance_threshold: int, default: 250
        Minimum time in milliseconds since last peak for a new peak to be registered.
    n_required_peaks: int, default: 3
        Minimum number of peaks in a window required to record analysis for that window.
        Values less than three are invalid.
    outlier_detection: str or OutlierDetectionSettings, default: "moderate"
        Settings for the Outlier detection algorithm.
        Accepts either an `OutlierDetectionSettings` object, or a string specifying a method.
        Refer to :class:`OutlierDetectionSettings` for details.

    Returns
    -------
    Dataframe containing Extracted heart data.
    """
    # Validate arguments
    outlier_detection_settings = (
        OutlierDetectionSettings.from_method(outlier_detection)
        if isinstance(outlier_detection, str)
        else outlier_detection
    )

    if n_required_peaks < 3:
        raise ValueError("Parameter 'n_required_peaks' must be greater than three.")

    # Peak detection settings
    if ecg_prt_clustering:
        distance = 1
        prominance = 5
        k = 3
    else:
        distance = distance_threshold
        prominance = amplitude_threshold
        k = 1

    # Windowing function
    for sample_start in range(0, input_data.size, (window_width - window_overlap) * sampling_rate):
        segment = input_data[sample_start : sample_start + (window_width * sampling_rate)]
        normalized = normalize(segment) * 100
        peak_detection(segment, distance=distance, prominance=prominance, k=k)
        break

    pass
