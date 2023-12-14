# Outputs

The output of this app aims to follow the guideline
of the [BIDS extension proposal 17 - Generic BIDS connectivity data schema](https://bids.neuroimaging.io/bep017).

Metadata files content is described in this BIDS extension proposal.

## participant level

When performing `participant` level analysis, the output is a HDF5 file per participant that was passed to `--participant_label` or all subjects under `bids_dir`.

The output file name is:

```
sub-<participant_id>/func/sub-<participant_id>_atlas-<atlas_name>_meas-PearsonCorrelation_desc-<denoising_strategy>_relmat.h5
```

## group level

When performing `group` level analysis,
the file will contain time series and connectomes of each subject,
as well as group average connectomes.

The output is a HDF5 file per participant that was passed to `--participant_label` or all subjects under `bids_dir`.

The output file name is: `group/atlas-<atlas_name>_meas-PearsonCorrelation_desc-<denoising_strategy>.h5`

## Examples

```
├── dataset_description.json
├── meas-PearsonCorrelation_desc-simple_relmat.json
├── group
│   └── atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-simple_relmat.h5
├── sub-1
│   └── func
│       └── sub-1_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-simple_relmat.h5
└── sub-2
    └── func
        └── sub-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-simple_relmat.h5
```

### BIDS compliant output

If the `--output_to_bids` is passed to the command line then each input file will have associated output file.

The output file name is:

```
sub-<participant_id>/[ses-<ses_id>]/func/<source_filename>_atlas-<atlas_name>_meas-PearsonCorrelation_desc-<denoising_strategy>_relmat.h5
```

Example:

```
giga_connectome/data/test_data/output
├── dataset_description.json
├── meas-PearsonCorrelation_desc-simple_relmat.json
├── group
│   └── atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-simple_relmat.h5
├── sub-1
│   ├── ses-timepoint1
│   │   └── func
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-simple_relmat.h5
│   │       └── sub-1_ses-timepoint1_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-simple_relmat.h5
│   └── ses-timepoint2
│       └── func
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-simple_relmat.h5
│           └── sub-1_ses-timepoint2_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-simple_relmat.h5
└── sub-2
    ├── ses-timepoint1
    │   └── func
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-simple_relmat.h5
    │       └── sub-2_ses-timepoint1_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-simple_relmat.h5
    └── ses-timepoint2
        └── func
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-simple_relmat.h5
            └── sub-2_ses-timepoint2_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-simple_relmat.h5
```
