import numpy as np
import rapidhrv as rhv


def test_pipeline():
    """Basic smoke test"""
    signal = rhv.get_example_data()
    preprocessed = rhv.preprocess(signal)
    result = rhv.analyze(preprocessed)
    bpm = np.nanmean(result['BPM'])
    rmssd = np.nanmean(result['RMSSD'])

    assert result is not None
    assert len(result) > 0
    assert not np.all(np.isnan(result["BPM"]))
    assert (59 < bpm < 61)
    assert (26 < rmssd < 28)

