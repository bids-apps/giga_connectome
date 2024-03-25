# Outputs

The output of this app aims to follow the guideline
of the [BIDS extension proposal 17 - Generic BIDS connectivity data schema](https://bids.neuroimaging.io/bep017).

Metadata files content is described in this BIDS extension proposal.

## Participant level

For each participant that was passed to `--participant_label`
(or all participants under `bids_dir` if no `--participant_label` is passed),
the output will be save in `sub-<participant_id>/[ses-<ses_id>]/func`.

### Data files

For each input image (that is, preprocessed BOLD time series)
and each atlas the following data files will be generated

- a `[matches]_atlas-{atlas}_meas-PearsonCorrelation_desc-{atlas_description}{denoise_strategy}_relmat.tsv`
  file that contains the correlation matrix between all the regions of the atlas
- a `[matches]_atlas-{atlas}_meas-PearsonCorrelation_desc-{atlas description}{denoise_strategy}_timeseries.tsv`
  file that contains the extracted timeseries for each region of the atlas

- `{atlas}` refers to the name of the atlas used (for example, `Schaefer20187Networks`)
- `{atlas_description}` refers to the sub type of atlas used (for example, `100Parcels7Networks`)
- `{denoise_strategy}` refers to the denoise strategy passed to the command line

### Metadata

A JSON file is generated in the root of the output dataset (`meas-PearsonCorrelation_relmat.json`)
that contains metadata applicable to all `relmat.tsv` files.

For each input image (that is, preprocessed BOLD time series)
a `[matches]_atlas-{atlas}_timeseries.json`

### Example

```
├── dataset_description.json
├── logs
│   └── CITATION.md
├── meas-PearsonCorrelation_relmat.json
├── sub-1
│   ├── ses-timepoint1
│   │   └── func
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-100Parcels7NetworksSimple_timeseries.tsv
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-200Parcels7NetworksSimple_timeseries.tsv
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-100Parcels7NetworksSimple_relmat.tsv
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-200Parcels7NetworksSimple_relmat.tsv
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_timeseries.json
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-100Parcels7NetworksSimple_timeseries.tsv
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-200Parcels7NetworksSimple_timeseries.tsv
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-100Parcels7NetworksSimple_relmat.tsv
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-200Parcels7NetworksSimple_relmat.tsv
│   │       └── sub-1_ses-timepoint1_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_timeseries.json
│   └── ses-timepoint2
│       └── func
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-100Parcels7NetworksSimple_timeseries.tsv
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-200Parcels7NetworksSimple_timeseries.tsv
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-100Parcels7NetworksSimple_relmat.tsv
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-200Parcels7NetworksSimple_relmat.tsv
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_timeseries.json
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-100Parcels7NetworksSimple_timeseries.tsv
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-200Parcels7NetworksSimple_timeseries.tsv
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-100Parcels7NetworksSimple_relmat.tsv
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-200Parcels7NetworksSimple_relmat.tsv
│           └── sub-1_ses-timepoint2_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_timeseries.json
└── sub-2
    ├── ses-timepoint1
    │   └── func
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-100Parcels7NetworksSimple_timeseries.tsv
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-200Parcels7NetworksSimple_timeseries.tsv
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-100Parcels7NetworksSimple_relmat.tsv
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-200Parcels7NetworksSimple_relmat.tsv
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_timeseries.json
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-100Parcels7NetworksSimple_timeseries.tsv
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-200Parcels7NetworksSimple_timeseries.tsv
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-100Parcels7NetworksSimple_relmat.tsv
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-200Parcels7NetworksSimple_relmat.tsv
    │       └── sub-2_ses-timepoint1_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_timeseries.json
    └── ses-timepoint2
        └── func
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-100Parcels7NetworksSimple_timeseries.tsv
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-200Parcels7NetworksSimple_timeseries.tsv
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-100Parcels7NetworksSimple_relmat.tsv
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-200Parcels7NetworksSimple_relmat.tsv
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_timeseries.json
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-100Parcels7NetworksSimple_timeseries.tsv
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_desc-200Parcels7NetworksSimple_timeseries.tsv
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-100Parcels7NetworksSimple_relmat.tsv
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-200Parcels7NetworksSimple_relmat.tsv
            └── sub-2_ses-timepoint2_task-probabilisticclassification_run-02_space-MNI152NLin2009cAsym_res-2_atlas-Schaefer20187Networks_timeseries.json
```
