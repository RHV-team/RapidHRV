import dataclasses
from typing import Union

import numpy as np
import numpy.typing
import pandas as pd
import scipy.signal
import sklearn.cluster
import sklearn.preprocessing

from .data import OutlierDetectionSettings, Signal


def peak_detection(
    segment: np.ndarray, distance: int, prominence: int, use_clustering: bool
) -> tuple[np.ndarray, dict]:
    """Returns the indexes of detected peaks and associated properties."""
    peaks, properties = scipy.signal.find_peaks(
        segment, distance=distance, prominence=prominence, height=0, width=0
    )
    n_peaks = len(peaks)

    # Attempt to determine correct peaks by distinguishing the R wave from P and T waves
    # @PeterKirk, which type of wave is this trying to determine?
    if len(peaks) >= 3 and use_clustering:
        kmeans = sklearn.cluster.KMeans(n_clusters=3).fit(
            np.column_stack(
                (properties["widths"], properties["peak_heights"], properties["prominences"])
            )
        )

        # Use width centroids to determine correct wave (least width, most prominence)
        # If the two lowest values are too close (< 5), use prominence to distinguish them
        width_cen = kmeans.cluster_centers_[:, 0]
        labels_sort_width = np.argsort(width_cen)
        if width_cen[labels_sort_width[1]] - width_cen[labels_sort_width[0]] < 5:
            # Label of maximum prominence for lowest two widths
            prom_cen = kmeans.cluster_centers_[:, 2]
            wave_label = np.argsort(prom_cen[labels_sort_width[:2]])[1]
        else:
            wave_label = labels_sort_width[0]

        is_wave_peak = kmeans.labels_ == wave_label

        wave_peaks = peaks[is_wave_peak]
        wave_props = {k: v[is_wave_peak] for k, v in properties.items()}
    else:
        wave_peaks = peaks
        wave_props = properties

    # @PeterKirk does this need to be > 3 or >= 3?
    # Also, should this potentially be done before clustering?
    if len(peaks) > 3:
        # Approximate prominences at edges of window
        base_height = segment[wave_peaks] - wave_props["prominences"]
        wave_props["prominences"][0] = wave_props["peak_heights"][0] - base_height[1]
        wave_props["prominences"][-1] = wave_props["peak_heights"][-1] - base_height[-2]

    return wave_peaks, wave_props


def analyze(
    signal: Signal,
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
        prominence = 5
    else:
        distance = int((distance_threshold / 1000) * signal.sample_rate)
        prominence = amplitude_threshold

    # Windowing function
    for sample_start in range(
        0, len(signal.data), (window_width - window_overlap) * signal.sample_rate
    ):
        segment = signal.data[sample_start : sample_start + (window_width * signal.sample_rate)]
        normalized = sklearn.preprocessing.minmax_scale(segment, (0, 100))
        peaks, properties = peak_detection(normalized, distance, prominence, ecg_prt_clustering)

    pass
