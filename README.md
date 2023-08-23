[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/github/SIMEXP/giga_connectome/branch/main/graph/badge.svg?token=TYE4UURNTQ)](https://codecov.io/github/SIMEXP/giga_auto_qc)

# giga_connectome

This is a BIDS-App to extract signal from a parcellation with nilearn,
typically useful in a context of resting-state data processing.

## Description

Functional connectivity is a common approach in analysing resting state fMRI data. Python tool Nilearn
provides utilities to extract, denoise time-series on a parcellation and compute functional connectivity.
Currently there's no standalone one stop solution to generate connectomes from fMRIPrep outputs.
This BIDS-app combines Nilearn, TemplateFlow to denoise the data and generate timeseries and functional
connectomes directly from fMRIPrep outputs.
The workflow comes with several built in denoising strategies and three choices of atlases
(MIST, Schaefer 7 networks, DiFuMo).
Users can customise their own strategies and atlases using the configuration json files.

## Usage

```
giga_connectome [-h] [-v] [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
                [-w WORK_DIR] [--atlas ATLAS] [--denoise-strategy DENOISE_STRATEGY]
                [--standardize {zscore,psc}] [--smoothing_fwhm SMOOTHING_FWHM]
                bids_dir output_dir {participant,group}

Generate connectome based on denoising strategy for fmriprep processed dataset.

positional arguments:
  bids_dir              The directory with the input dataset (e.g. fMRIPrep derivative)formatted
                        according to the BIDS standard.
  output_dir            The directory where the output files should be stored.
  {participant,group}   Level of the analysis that will be performed.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
                        The label(s) of the participant(s) that should be analyzed. The label
                        corresponds to sub-<participant_label> from the BIDS spec
                        (so it does not include 'sub-'). If this parameter is not provided all
                        subjects should be analyzed. Multiple participants can be specified with
                        a space separated list.
  -w WORK_DIR, --work-dir WORK_DIR
                        Path where intermediate results should be stored.
  --atlas ATLAS         The choice of atlas for time series extraction. Default atlas choices
                        are: 'Schaefer20187Networks, 'MIST', 'DiFuMo'. User can pass a path to a
                        json file containing configuration for their own choice of atlas.
                        The default is 'DiFuMo'.
  --denoise-strategy DENOISE_STRATEGY
                        The choice of post-processing for denoising. The default choices are:
                        'simple', 'simple+gsr', 'scrubbing.2', 'scrubbing.2+gsr', 'scrubbing.5',
                        'scrubbing.5+gsr', 'acompcor50', 'icaaroma'.
                        User can pass a path to a json file containing configuration for their
                        own choice of denoising strategy.
                        The defaultis 'simple'.
  --standardize {zscore,psc}
                        The choice of signal standardization. The choices are z score or
                        percent signal change (psc).
                        The default is 'zscore'.
  --smoothing_fwhm SMOOTHING_FWHM
                        Size of the full-width at half maximum in millimeters of the spatial
                        smoothing to apply to the signal.
                        The default is 5.0.

```

When performing `participant` level analysis, the output is a HDF5 file per participant that was passed to `--participant_label` or all subjects under `bids_dir`.
The output file name is: `sub-<participant_id>[_ses-<session>]_task-<task>[_run-<run>]_space-<template>_atlas-<atlas_name>_desc-<denoising_strategy>.h5`

When performing `group` level analysis, the output is a HDF5 file per participant that was passed to `--participant_label` or all subjects under `bids_dir`.
The output file name is: `atlas-<atlas_name>_desc-<denoising_strategy>.h5`
The file will contain time series and connectomes of each subject, as well as group average connectomes.

## Writing configuration files

All preset can be found in `giga_connectome/data`

### Denoising strategy

The tool uses `nilearn.interfaces.fmriprep.load_confounds` and `nilearn.interfaces.fmriprep.load_confounds_strategy`
as the way of retrieving confounds.

In a `json` file, define the customised strategy in the following format:

```
{
    "name": "<name_of_the_strategy>",
    "function": "<load_confounds>, <load_confounds_strategy>",
    "parameters": {
        "<function_parameters>": "<options>",
        ....
    }
}
```

See examples in `giga_connectome/data/denoise_strategy`.

### Atlas

After the atlas files are organised according to the [TemplateFlow](https://www.templateflow.org/python-client/0.7.1/naming.html) convention.

A minimal set up should look like this:
```
my_atlas/
  └──tpl-MNI152NLin2009cAsym/  # template directory of a valid template name
      ├── tpl-MNI152NLin2009cAsym_res-02_atlas-coolatlas_desc-256dimensions_probseg.nii.gz
      ├── tpl-MNI152NLin2009cAsym_res-02_atlas-coolatlas_desc-512dimensions_probseg.nii.gz
      └── tpl-MNI152NLin2009cAsym_res-02_atlas-coolatlas_desc-64dimensions_probseg.nii.gz
```

In a `json` file, define the customised atlas. We will use the atlas above as an example:

```
{
    "name": "<name_of_atlas>",
    "parameters": {  # the fields in this section should all be present and consistent with your atlas, except 'desc'
        "atlas": "coolatlas",
        "template": "MNI152NLin2009cAsym",
        "resolution": "02",
        "suffix": "probseg"
    },
    "desc": [  # entity desc of the atlases
        "64dimensions",
        "128dimensions",
        "256dimensions"],
    "templateflow_dir" : "my_atlas/"  # To use the default templateflow directory, set value to null
}
```

See examples in `giga_connectome/data/atlas`.

## Workflow

1. Create group level / subject specific grey matter mask in MNI space.

2. Sample the atlas to the space of group level  / subject specific grey matter mask in MNI space.

3. Calculate the conjunction of the customised grey matter mask and resampled atlas to find valid parcels.

4. Use the new input specific grey matter mask and atlas to extract time series and connectomes for each subject.

5. Create a group average connectome (if analysis level is `group`).

## How to report errors

Please use the [GitHub issue](https://github.com/SIMEXP/giga_connectome/issues) to report errors.
Check out the open issues first to see if we're already working on it.
If not, [open up a new issue](https://github.com/SIMEXP/giga_connectome/issues/new)!

## How to contribute

You can review open [issues]((https://github.com/SIMEXP/giga_connectome/issues)) that we are looking for help with.
If you submit a new pull request please be as detailed as possible in your comments.

## Installation

```
pip install .
```

For development:
```
pip install -e .[dev]
```

## Usage

```
giga_connectome [-h] [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]] [-w WORK_DIR] [--atlas ATLAS] [--denoise-strategy DENOISE_STRATEGY] [--bids-filter-file BIDS_FILTER_FILE] bids_dir output_dir {participant,group}

Generate connectome based on denoising strategy for fmriprep processed dataset.

positional arguments:
  bids_dir              The directory with the input dataset (e.g. fMRIPrep derivative)formatted according to the BIDS standard.
  output_dir            The directory where the output files should be stored.
  {participant,group}   Level of the analysis that will be performed.

optional arguments:
  -h, --help            show this help message and exit
  --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
                        The label(s) of the participant(s) that should be analyzed. The label corresponds to sub-<participant_label> from the BIDS spec (so it does not include 'sub-'). If this parameter is not provided all subjects should be analyzed. Multiple participants can be specified with a space separated list.
  -w WORK_DIR, --work-dir WORK_DIR
                        Path where intermediate results should be stored.
  --atlas ATLAS         The choice of atlas for time series extraction. Default atlas choices are: 'Schaefer20187Networks, 'MIST', 'DiFuMo'. User can pass a path to a json file containing configuration for their own choice of atlas.
  --denoise-strategy DENOISE_STRATEGY
                        The choice of post-processing for denoising. The default choices are: 'simple', 'simple+gsr', 'scrubbing.2', 'scrubbing.2+gsr', 'scrubbing.5', 'scrubbing.5+gsr', 'acompcor50', 'icaaroma'. User can pass a path to a json file containing configuration for their own choice of denoising strategy.

```

When performing `participant` level analysis, the output is a HDF5 file per participant that was
passed to `--participant_label` or all subjects under `bids_dir`.
The output file name is:
`sub-<participant_id>[_ses-<session>]_task-<task>[_run-<run>]_space-<template>_atlas-<atlas_name>_desc-<denoising_strategy>.h5`

When performing `group` level analysis, the output is a HDF5 file per participant that was passed
to `--participant_label` or all subjects under `bids_dir`.
The output file name is: `atlas-<atlas_name>_desc-<denoising_strategy>.h5`
The file will contain time series and connectomes of each subject, as well as group average connectomes.

## Acknowledgements

If you use nilearn, please cite the corresponding paper: Abraham 2014,
Front. Neuroinform., Machine learning for neuroimaging with scikit-learn
http://dx.doi.org/10.3389/fninf.2014.00014

We acknowledge all the nilearn developers
(https://github.com/nilearn/nilearn/graphs/contributors)
as well as the BIDS-Apps team
https://github.com/orgs/BIDS-Apps/people

This is a Python project packaged according to [Contemporary Python Packaging - 2023][].

[Contemporary Python Packaging - 2023]: https://effigies.gitlab.io/posts/python-packaging-2023/
