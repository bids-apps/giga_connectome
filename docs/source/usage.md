# Usage Notes

```bash
usage: giga_connectome [-h] [-v] [--participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]] [-w WORK_DIR] [--atlas ATLAS]
                       [--denoise-strategy DENOISE_STRATEGY] [--standardize {zscore,psc}] [--smoothing_fwhm SMOOTHING_FWHM] [--reindex-bids]
                       [--bids-filter-file BIDS_FILTER_FILE]
                       bids_dir output_dir {participant,group}

Generate connectome based on denoising strategy for fmriprep processed dataset.

positional arguments:
  bids_dir              The directory with the input dataset (e.g. fMRIPrep derivative)formatted according to the BIDS standard.
  output_dir            The directory where the output files should be stored.
  {participant,group}   Level of the analysis that will be performed. Only group level is allowed as we need to generate a dataset inclusive brain mask.

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  --participant_label PARTICIPANT_LABEL [PARTICIPANT_LABEL ...]
                        The label(s) of the participant(s) that should be analyzed. The label corresponds to sub-<participant_label> from the BIDS spec (so it does not include 'sub-'). If this parameter is not provided all subjects should be analyzed. Multiple participants can be specified with a space separated list.
  -w WORK_DIR, --work-dir WORK_DIR
                        Path where intermediate results should be stored.
  --atlas ATLAS         The choice of atlas for time series extraction. Default atlas choices are: 'Schaefer20187Networks, 'MIST', 'DiFuMo'. User can pass a path to a json file containing configuration for their own choice of atlas. The default is 'MIST'.
  --denoise-strategy DENOISE_STRATEGY
                        The choice of post-processing for denoising. The default choices are: 'simple', 'simple+gsr', 'scrubbing.2', 'scrubbing.2+gsr', 'scrubbing.5', 'scrubbing.5+gsr', 'acompcor50', 'icaaroma'. User can pass a path to a json file containing configuration for their own choice of denoising strategy. The defaultis 'simple'.
  --standardize {zscore,psc}
                        The choice of signal standardization. The choices are z score or percent signal change (psc). The default is 'zscore'.
  --smoothing_fwhm SMOOTHING_FWHM
                        Size of the full-width at half maximum in millimeters of the spatial smoothing to apply to the signal. The default is 5.0.
  --reindex-bids        Reindex BIDS data set, even if layout has already been created.
  --bids-filter-file BIDS_FILTER_FILE
                        A JSON file describing custom BIDS input filters using PyBIDS.We use the same format as described in fMRIPrep documentation: https://fmriprep.org/en/latest/faq.html#how-do-i-select-only-certain-files-to-be-input-to-fmriprepHowever, the query filed should always be 'bold'

```

When performing `participant` level analysis, the output is a HDF5 file per participant that was passed to `--participant_label` or all subjects under `bids_dir`.
The output file name is: `sub-<participant_id>_atlas-<atlas_name>_desc-<denoising_strategy>.h5`

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
