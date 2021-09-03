from __future__ import annotations

import dataclasses
import io
import pathlib
from typing import Union

import h5py
import numpy as np
import numpy.typing


@dataclasses.dataclass
class OutlierDetectionSettings:
    """Settings for outlier detection.

    Attributes
    ----------
    bpm_range:
        Range of acceptable bpm values.
    rmssd_range:
        Range of acceptable rmssd values.
    mad_threshold:
        Threshold (in median absolute deviation units) for peak heights and prominences to register as outliers.
    ibi_mad_threshold:
        Threshold (in median absolute deviation units) for peak intervals to register as an outliers.
    min_total_peak_distance:
        Acceptable ratio between total width to distance between first and last peaks in window.
    """

    bpm_range: tuple[int, int]
    rmssd_range: tuple[int, int]
    mad_threshold: int
    ibi_mad_threshold: int
    min_total_peak_distance: float = 0.5

    @classmethod
    def from_method(cls, method: str) -> OutlierDetectionSettings:
        """Generate settings from method name.

        Method names are: "liberal", "moderate", "conservative".
        "conservative" is the most stringent, "liberal" is the least and "moderate" is in-between.
        """
        if method == "liberal":
            return OutlierDetectionSettings(
                bpm_range=(20, 200), rmssd_range=(0, 300), mad_threshold=7, ibi_mad_threshold=7
            )
        elif method == "moderate":
            return OutlierDetectionSettings(
                bpm_range=(30, 190), rmssd_range=(5, 262), mad_threshold=5, ibi_mad_threshold=5
            )
        elif method == "conservative":
            return OutlierDetectionSettings(
                bpm_range=(40, 180), rmssd_range=(10, 200), mad_threshold=4, ibi_mad_threshold=4
            )
        else:
            raise RuntimeError(f"Invalid outlier detection method: {method}.")


@dataclasses.dataclass
class Signal:
    """Raw signal with associated metadata.

    Attributes
    ----------
    data:
        Raw signal data.
    sample_rate:
        Signal rate in Hertz of raw signal.
    """

    data: np.ndarray
    sample_rate: int

    def __post_init__(self):
        self.data = self.data if isinstance(self.data, np.ndarray) else np.array(self.data)

    def save(self, filename: str) -> None:
        """Save as filename.hdf5"""
        with h5py.File(filename, "w") as f:
            f["data"] = self.data
            f.attrs["sample_rate"] = self.sample_rate

    @classmethod
    def load(cls, filename: str) -> Signal:
        """Load from filename.hdf5"""
        with h5py.File(filename, "r") as f:
            return cls(
                data=f["data"],
                sample_rate=int(f.attrs["sample_rate"]),
            )


def get_example_data():
    """Function to get example data from github

    Returns
    -------
    array_like
        example data
    """
    url = 'https://github.com/peterakirk/RapidHRV/tree/refactor/resources/example_data.csv'
    data = pd.read_csv(url, index_col=0, parse_dates=[0])
    return data
