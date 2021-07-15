from typing import Literal, Optional

import numpy as np
import numpy.typing
from scipy import interpolate, signal  # type: ignore


def cubic_spline_interpolation(
    input_data: np.ndarray, sampling_rate: int, resample_rate: int
) -> np.ndarray:
    if resample_rate % sampling_rate != 0:
        raise RuntimeError(
            f"Cannot resample from {sampling_rate = }Hz to {resample_rate = }Hz: "
            f"{resample_rate % sampling_rate = } must be zero."
        )

    sample_ratio = resample_rate / sampling_rate
    result_size = input_data.size * sample_ratio
    # @PeterKirk
    # I have compared the output of this function to that of the FITPACK fns used previously
    # and they are equivalent
    # Documentation suggests using this method over the FITPACK version in modern code
    # (see splev docs)
    b_spline = interpolate.make_interp_spline(np.arange(0, result_size, sample_ratio), input_data)
    return b_spline(np.arange(0, result_size))


def butterworth_filter(
    input_data: np.ndarray,
    cutoff_freq: float,
    sampling_rate: int,
    filter_type: Literal["highpass", "lowpass"],
) -> np.ndarray:
    nyquist_freq = sampling_rate / 2
    # @PeterKirk
    # Consider maybe using sos filter type?
    # Documentation says it is more stable, but it produces slightly different results
    # Also, the following pycharm inspection suppression is no longer required with sos
    # Follow-up: when preceded by interpolation, results differ from original results even with b, a filter
    # Likely due to aforementioned numerical inconsistencies. Differences are small though,
    # 1.3e-6 avg and and 2.9e-3 99th percentile difference in abs value from output of original pipeline
    sos = signal.butter(N=5, Wn=(cutoff_freq / nyquist_freq), btype=filter_type, output="sos")
    return signal.sosfiltfilt(sos, input_data)


def sg_filter(
    input_data: np.ndarray, sampling_rate: int, sg_settings: tuple[int, int]
) -> np.ndarray:
    poly_order, smoothing_window_ms = sg_settings
    # @PeterKirk
    # You may have had a bit of a bug... remember, x / (x / y) == y
    # I think the code worked in on your test cases because your default resampling rate is 1000Hz
    # which just happens to be how many milliseconds there are in a second...
    # convert to seconds, then samples
    smoothing_window = (smoothing_window_ms / 1000) * sampling_rate
    smoothing_window = round(smoothing_window)

    # smoothing_window must be odd
    if smoothing_window % 2 == 0:
        smoothing_window += 1

    return signal.savgol_filter(input_data, smoothing_window, poly_order)


def preprocess(
    input_data: np.typing.ArrayLike,
    sampling_rate: int,
    resample_rate: Optional[int] = 1000,
    highpass_cutoff: Optional[float] = 0.5,
    lowpass_cutoff: Optional[float] = None,
    sg_settings: Optional[tuple[int, int]] = (3, 100),
) -> np.ndarray:
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
    input_data : array_like
        Cardiac data to be processed.
    sampling_rate : int
        Sampling rate of `input_data` in hertz.
    resample_rate : int, default: 1000
        If greater than `sampling_rate`,
        will be used as the target sample rate (hertz) for cubic spline interpolation.
        Must be divisible by `sampling_rate`.
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
    nans = np.isnan(input_data)
    if np.any(nans):
        raise RuntimeError(
            "Cannot preprocess data containing NaN values. "
            f"First NaN found at index {nans.nonzero()[0][0]}."
        )

    result = input_data if isinstance(input_data, np.ndarray) else np.array(input_data)

    if resample_rate is not None and resample_rate > sampling_rate:
        result = cubic_spline_interpolation(result, sampling_rate, resample_rate)
        sampling_rate = resample_rate

    if highpass_cutoff is not None:
        result = butterworth_filter(result, highpass_cutoff, sampling_rate, "highpass")

    if lowpass_cutoff is not None:
        result = butterworth_filter(result, lowpass_cutoff, sampling_rate, "lowpass")

    if sg_settings:
        result = sg_filter(result, sampling_rate, sg_settings)

    return result
