import os
import pathlib
import unittest

import numpy as np
import rapidhrv as rhv

RESOURCES_FOLDER = pathlib.Path(os.path.dirname(os.path.realpath(__file__))).parent / "resources"


class TestRapidHRV(unittest.TestCase):
    def test_pipeline(self):
        example_data = np.load(str(RESOURCES_FOLDER / "example_data.npy"))
        signal = rhv.Signal(data=example_data, sample_rate=20)
        preprocessed = rhv.preprocess(signal)
        result = rhv.analyze(preprocessed)
        self.assertIsNotNone(result)
        self.assertTrue(len(result) > 0)
        self.assertFalse(np.all(np.isnan(result["CleanedBPM"])))
