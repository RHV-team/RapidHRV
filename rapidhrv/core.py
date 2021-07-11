from typing import Optional

import dataclasses


@dataclasses.dataclass
class SGFilterSettings:
    polynomial_order: int = 3
    smoothing_window: int = 100


@dataclasses.dataclass
class RapidHRVSettings:
    sampling_rate: int
    resample_rate: int = 1000
    frequency_band: tuple[Optional[float], Optional[float]] = (0.5, None)
    sg_filter: Optional[SGFilterSettings] = SGFilterSettings()

