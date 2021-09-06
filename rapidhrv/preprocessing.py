import dataclasses
from typing import Literal, Optional

import numpy as np
import scipy.interpolate
import scipy.signal

from .data import Signal


def cubic_spline_interpolation(signal: Signal, resample_rate: int) -> Signal:
    if resample_rate % signal.sample_rate != 0:
        raise RuntimeError(
            f"Cannot resample from {signal.sample_rate = }Hz to {resample_rate = }Hz: "
            f"{resample_rate % signal.sample_rate = } must be zero."
        )

    sample_ratio = resample_rate / signal.sample_rate
    result_size = len(signal.data) * sample_ratio
    b_spline = scipy.interpolate.make_interp_spline(
        np.arange(0, result_size, sample_ratio), signal.data
    )
    return Signal(data=b_spline(np.arange(0, result_size)), sample_rate=resample_rate)


def butterworth_filter(
    signal: Signal,
    cutoff_freq: float,
    filter_type: Literal["highpass", "lowpass"],
) -> Signal:
    nyquist_freq = signal.sample_rate / 2
    sos = scipy.signal.butter(
        N=5, Wn=(cutoff_freq / nyquist_freq), btype=filter_type, output="sos"
    )
    return dataclasses.replace(signal, data=scipy.signal.sosfiltfilt(sos, signal.data))


def sg_filter(signal: Signal, sg_settings: tuple[int, int]) -> Signal:
    poly_order, smoothing_window_ms = sg_settings
    smoothing_window = (smoothing_window_ms / 1000) * signal.sample_rate
    smoothing_window = round(smoothing_window)

    # smoothing_window must be odd
    if smoothing_window % 2 == 0:
        smoothing_window += 1

    return dataclasses.replace(
        signal, data=scipy.signal.savgol_filter(signal.data, smoothing_window, poly_order)
    )


def preprocess(
    signal: Signal,
    resample_rate: Optional[int] = 1000,
    highpass_cutoff: Optional[float] = 0.5,
    lowpass_cutoff: Optional[float] = None,
    sg_settings: Optional[tuple[int, int]] = (3, 100),
) -> Signal:
    """Prepares cardiac data for analysis using global functions.

    Applies in order:
    cubic spline interpolation,
    highpass and lowpass Butterworth filters
    and Savitzky-Golay smoothing.

    Parameters set to None imply that aspect of the pipeline will not be applied.
    For example, the default value for `lowpass_cutoff` is None,
    which implies that by default the lowpass filter will not be applied.

    Parameters
    ----------
    signal : Signal
        Cardiac signal to be processed.
    resample_rate : int, default: 1000
        If greater than `signal.sample_rate`,
        will be used as the target sample rate (hertz) for cubic spline interpolation.
        Must be divisible by `signal.sample_rate`.
    highpass_cutoff : float, default: 0.5
        Butterworth highpass filter cutoff frequency in hertz.
    lowpass_cutoff : float, optional
        Butterworth lowpass filter cutoff frequency in Hertz, filter is off by default.
    sg_settings : (int, int), default: (3, 100)
        Savitzky-Golay smoothing parameters,
        where the first element of the tuple is the polynomial order
        and the second is the window size in milliseconds.

    Returns
    -------
    array_like
        Preprocessed signal
    """
    nans = np.isnan(signal.data)
    if np.any(nans):
        raise RuntimeError(
            "Cannot preprocess data containing NaN values. "
            f"First NaN found at index {nans.nonzero()[0][0]}."
        )

    if resample_rate is not None and resample_rate > signal.sample_rate:
        result = cubic_spline_interpolation(signal, resample_rate)
    else:
        result = signal

    if highpass_cutoff is not None:
        result = butterworth_filter(result, highpass_cutoff, "highpass")

    if lowpass_cutoff is not None:
        result = butterworth_filter(result, lowpass_cutoff, "lowpass")

    if sg_settings:
        result = sg_filter(result, sg_settings)

    return result
