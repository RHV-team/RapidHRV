import numpy as np

import rapidhrv as rhv


def test_pipeline():
    """Basic smoke test"""
    signal = rhv.get_example_data()
    preprocessed = rhv.preprocess(signal)
    result = rhv.analyze(preprocessed)
    assert result is not None
    assert len(result) > 0
    assert not np.all(np.isnan(result["BPM"]))
