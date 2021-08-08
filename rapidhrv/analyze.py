from __future__ import annotations

import dataclasses
from typing import Literal, Union

import numpy as np
import numpy.typing
import pandas as pd


@dataclasses.dataclass
class OutlierDetectionSettings:
    """Settings for outlier detection."""

    bpm_range: tuple[int, int]
    rmssd_range: tuple[int, int]
    mad: int
    ibi_mad: int
    min_inter_peak_distance: float = 0.5

    @classmethod
    def from_method(
        cls, method: Literal["liberal", "moderate", "conservative"]
    ) -> OutlierDetectionSettings:
        """Generate settings from method name.

        Method names are: "liberal", "moderate", "conservative".
        "conservative" is the most stringent, "liberal" is the least and "moderate" is in-between.
        """
        if method == "liberal":
            return OutlierDetectionSettings(
                bpm_range=(20, 200), rmssd_range=(0, 300), mad=7, ibi_mad=7
            )
        elif method == "moderate":
            return OutlierDetectionSettings(
                bpm_range=(30, 190), rmssd_range=(5, 262), mad=5, ibi_mad=5
            )
        elif method == "conservative":
            return OutlierDetectionSettings(
                bpm_range=(40, 180), rmssd_range=(10, 200), mad=4, ibi_mad=4
            )
        else:
            raise RuntimeError(f"Invalid outlier detection method: {method}.")


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
    # validate arguments
    if n_required_peaks < 3:
        raise ValueError("Parameter 'n_required_peaks' must be greater than three.")

    for sample_start in range(0, input_data.size, (window_width - window_overlap) * sampling_rate):
        segment = input_data[sample_start : sample_start + (window_width * sampling_rate)]

    pass
