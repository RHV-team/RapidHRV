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
    """Settings for outlier detection."""

    bpm_range: tuple[int, int]
    rmssd_range: tuple[int, int]
    mad: int
    ibi_mad: int
    min_inter_peak_distance: float = 0.5

    @classmethod
    def from_method(cls, method: str) -> OutlierDetectionSettings:
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


@dataclasses.dataclass
class Signal:
    """Raw signal with associated metadata."""

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
