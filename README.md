[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/SIMEXP/giga_connectome/branch/main/graph/badge.svg?token=P4EGV7NKZ8)](https://codecov.io/gh/SIMEXP/giga_connectome)
# giga_connectome

BIDS App to generate connectome from fMRIPrep outputs.

This is a Python project packaged according to [Contemporary Python Packaging - 2023][].

[Contemporary Python Packaging - 2023]: https://effigies.gitlab.io/posts/python-packaging-2023/

## Usage

```
giga_connectome [-h] [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]]
  [-w WORK_DIR] [--atlas ATLAS] [--denoise-strategy DENOISE_STRATEGY]
  [--bids-filter-file BIDS_FILTER_FILE]
  bids_dir output_dir {participant,group}

Generate connectome based on denoising strategy for fmriprep processed dataset.

positional arguments:
  bids_dir              The directory with the input dataset (e.g. fMRIPrep derivative)
                          formatted according to the BIDS standard.
  output_dir            The directory where the output files should be stored.
  {participant,group}   Level of the analysis that will be performed.

optional arguments:
  -h, --help            show this help message and exit
  --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
                        The label(s) of the participant(s) that should be analyzed. The
                          label corresponds to sub-<participant_label> from the BIDS spec
                          (so it does not include 'sub-'). If this parameter is not provided
                          all subjects should be analyzed. Multiple participants can be
                          specified with a space separated list.
  -w WORK_DIR, --work-dir WORK_DIR
                        Path where intermediate results should be stored.
  --atlas ATLAS         The choice of atlas for time series extraction. Default atlas choices
                          are: 'Schaefer20187Networks, 'MIST', 'DiFuMo'.
                          User can pass a path to a json file containing configuration for
                          their own choice of atlas.
  --denoise-strategy DENOISE_STRATEGY
                        The choice of post-processing for denoising. The default choices are:
                          'simple', 'simple+gsr', 'scrubbing.2', 'scrubbing.2+gsr',
                          'scrubbing.5', 'scrubbing.5+gsr', 'acompcor50', 'icaaroma'.
                          User can pass a path to a json file containing configuration for
                          their own choice of denoising strategy.

```

When performing `participant` level analysis, the output is a HDF5 file per participant that was passed to `--participant_label` or all subjects under `bids_dir`.
The output file name is: `sub-<participant_id>[_ses-<session>]_task-<task>[_run-<run>]_space-<template>_atlas-<atlas_name>_desc-<denoising_strategy>.h5`

When performing `group` level analysis, the output is a HDF5 file per participant that was passed to `--participant_label` or all subjects under `bids_dir`.
The output file name is: `atlas-<atlas_name>_desc-<denoising_strategy>.h5`
The file will contain time series and connectomes of each subject, as well as group average connectomes.

## Writing configuration files

All preset can be found in `giga_connectome/data`

### Denoising strategy

The tool uses `nilearn.interfaces.fmriprep.load_confounds` and `nilearn.interfaces.fmriprep.load_confounds_strategy` as the way of retrieving confounds.

TBA

### Atlas

The tool relies on atlases file naming matching the [TemplateFlow](https://www.templateflow.org/python-client/0.7.1/naming.html) convention.

TBA

## Workflow

1. Create group level / subject specific grey matter mask in MNI space.

2. Sample the atlas to the space of group level  / subject specific grey matter mask in MNI space.

3. Calculate the conjunction of the customised grey matter mask and resampled atlas to find valid parcels.

4. Use the new input specific grey matter mask and atlas to extract time series and connectomes for each subject.

5. Create a group average connectome (if analysis level is `group`).
