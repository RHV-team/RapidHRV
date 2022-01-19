# RapidHRV

RapidHRV is a data processing pipeline for the analysis and visualization of cardiac data.

Please provide credit where appropriate:

Kirk, P. A., Davidson Bryan, A., Garfinkel, S., & Robinson, O. J. (2021).
_RapidHRV: An open-source toolbox for extracting heart rate and heart rate variability_
([PsyArXiv](https://doi.org/10.31234/osf.io/3ewgz))

This library is distributed under an 
[MIT License](https://raw.githubusercontent.com/peterakirk/RapidHRV/main/LICENSE)

## Installation

```shell
pip install rapidhrv
```

## Usage

Given a numpy array, or something convertable to it (such as a list),
`rapidhrv.preprocess` can generate input suitable for analysis with
`rapidhrv.analyze`, which will return a pandas dataframe containing HRV data.

```python
import numpy as np
import rapidhrv as rhv

my_data = np.load("my_data.npy")  # Load data
data = rhv.Signal(my_data, sample_rate=50)  # Convert to rhv Signal class
preprocessed = rhv.preprocess(data)  # Preprocess: may interpolate data, check the docstring on `rapidhrv.preprocess`
result = rhv.analyze(preprocessed)  # Analyze signal
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

This project uses [Git LFS](https://git-lfs.github.com),
please install it for your platform before using the provided data files.
Run `git lfs fetch && git lfs checkout` after installing to populate the data files.

If you plan on making any changes to the included notebooks,
please run `nbstripout --install` from within the poetry venv before committing any changes.

To run said notebooks from the environment provided by poetry,
install the required dependencies with `poetry install --extras notebooks`.

