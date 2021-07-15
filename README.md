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
import rapidhrv

...
```

## Development

In order to get a working development environment,
please install [Poetry](https://python-poetry.org/) for your platform,
and run `poetry install`.

On MacOS, you may need to `export SYSTEM_VERSION_COMPAT=1` before `poetry install`ing.
Read [this blog post](https://eclecticlight.co/2020/08/13/macos-version-numbering-isnt-so-simple/)
for more details on why.

## Documentation

WIP: We will use https://readthedocs.org/ and sphinx to document the library
