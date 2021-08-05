# RapidHRV

RapidHRV is a data processing pipeline for the analysis and visualization of cardiac data
(validated on ECG, Pulse Oximetry, and PPG).

Please provide credit where appropriate:

Kirk, P. A., Garfinkel, S., & Robinson, O. J. (2021).
_RapidHRV: An open-source toolbox for extracting heart rate and heart rate variability_
([PsyArXiv](https://doi.org/10.31234/osf.io/3ewgz.))

This library is distributed under an 
[MIT License](https://raw.githubusercontent.com/peterakirk/RapidHRV/main/LICENSE)

## Installation

```shell
pip install rapidhrv
```

## Usage

```python
import numpy as np
import rapidhrv

my_data = np.load("my_data.npy")
preprocessed = rapidhrv.preprocess(my_data, sampling_rate=500)
result = rapidhrv.analyze(preprocessed, sampling_rate=1000)  # preprocess interpolates data by default
```

## Documentation

WIP: We will use https://readthedocs.org/ and sphinx to document the library

## Development

In order to get a working development environment,
please install [Poetry](https://python-poetry.org/) for your platform,
and run `poetry install` to generate a virtual environment.

On MacOS, you may need to `export SYSTEM_VERSION_COMPAT=1` before running `poetry install`.
Read [this blog post](https://eclecticlight.co/2020/08/13/macos-version-numbering-isnt-so-simple/)
for more details on why.

This project uses [Git LFS](git-lfs.github.com),
please install it for your platform before using the provided data files.
Run `git lfs checkout` after installing to populate the data files.

If you plan on making any changes to the included notebooks,
please run `nbstripout --install` from within the poetry venv before committing any changes.

To run said notebooks from the environment provided by poetry,
install the required dependencies with `poetry install --extras notebooks`.

