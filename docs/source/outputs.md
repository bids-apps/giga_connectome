# Outputs

The output of this app aims to follow the guideline
of the [BIDS extension proposal 17 - Generic BIDS connectivity data schema](https://bids.neuroimaging.io/bep017).

Metadata files content is described in this BIDS extension proposal.

## Participant level

For each participant that was passed to `--participant-label`
(or all participants under `bids_dir` if no `--participant-label` is passed),
the output will be save in `sub-<participant_id>/[ses-<ses_id>]/func`.

### Data files

For each input image (that is, preprocessed BOLD time series)
and each atlas the following data files will be generated

- a `[matches]_seg-{atlas}{atlas_description}_meas-PearsonCorrelation_desc-denoise{denoise_strategy}_relmat.tsv`
  file that contains the correlation matrix between all the regions of the atlas
- a `[matches]_seg-{atlas}{atlas_description}_desc-denoise{denoise_strategy}_timeseries.tsv`
  file that contains the extracted timeseries for each region of the atlas

- `{atlas}` refers to the name of the atlas used (for example, `Schaefer2018`)
- `{atlas_description}` refers to the sub type of atlas used (for example, `100Parcels7Networks`)
- `{denoise_strategy}` refers to the denoise strategy passed to the command line

### Metadata

A JSON file is generated in the root of the output dataset (`meas-PearsonCorrelation_relmat.json`)
that contains metadata applicable to all `relmat.tsv` files.

For each input image (that is, preprocessed BOLD time series)
a `[matches]_desc-denoise{denoise_strategy}_timeseries.json`

### Example

```
├── dataset_description.json
├── logs
│   └── CITATION.md
├── meas-PearsonCorrelation_relmat.json
├── sub-1
│   ├── ses-timepoint1
│   │   └── func
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-01_desc-denoiseSimple_timeseries.json
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-01_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_report.html
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-01_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_timeseries.tsv
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-01_seg-Schaefer2018100Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-01_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_report.html
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-01_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_timeseries.tsv
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-01_seg-Schaefer2018200Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-02_desc-denoiseSimple_timeseries.json
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-02_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_report.html
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-02_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_timeseries.tsv
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-02_seg-Schaefer2018100Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-02_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_report.html
│   │       ├── sub-1_ses-timepoint1_task-probabilisticclassification_run-02_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_timeseries.tsv
│   │       └── sub-1_ses-timepoint1_task-probabilisticclassification_run-02_seg-Schaefer2018200Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
│   └── ses-timepoint2
│       └── func
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-01_desc-denoiseSimple_timeseries.json
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-01_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_report.html
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-01_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_timeseries.tsv
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-01_seg-Schaefer2018100Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-01_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_report.html
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-01_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_timeseries.tsv
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-01_seg-Schaefer2018200Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-02_desc-denoiseSimple_timeseries.json
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-02_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_report.html
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-02_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_timeseries.tsv
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-02_seg-Schaefer2018100Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-02_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_report.html
│           ├── sub-1_ses-timepoint2_task-probabilisticclassification_run-02_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_timeseries.tsv
│           └── sub-1_ses-timepoint2_task-probabilisticclassification_run-02_seg-Schaefer2018200Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
└── sub-2
    ├── ses-timepoint1
    │   └── func
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-01_desc-denoiseSimple_timeseries.json
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-01_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_report.html
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-01_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_timeseries.tsv
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-01_seg-Schaefer2018100Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-01_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_report.html
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-01_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_timeseries.tsv
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-01_seg-Schaefer2018200Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-02_desc-denoiseSimple_timeseries.json
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-02_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_report.html
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-02_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_timeseries.tsv
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-02_seg-Schaefer2018100Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-02_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_report.html
    │       ├── sub-2_ses-timepoint1_task-probabilisticclassification_run-02_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_timeseries.tsv
    │       └── sub-2_ses-timepoint1_task-probabilisticclassification_run-02_seg-Schaefer2018200Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
    └── ses-timepoint2
        └── func
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-01_desc-denoiseSimple_timeseries.json
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-01_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_report.html
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-01_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_timeseries.tsv
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-01_seg-Schaefer2018100Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-01_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_report.html
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-01_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_timeseries.tsv
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-01_seg-Schaefer2018200Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-02_desc-denoiseSimple_timeseries.json
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-02_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_report.html
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-02_seg-Schaefer2018100Parcels7Networks_desc-denoiseSimple_timeseries.tsv
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-02_seg-Schaefer2018100Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-02_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_report.html
            ├── sub-2_ses-timepoint2_task-probabilisticclassification_run-02_seg-Schaefer2018200Parcels7Networks_desc-denoiseSimple_timeseries.tsv
            └── sub-2_ses-timepoint2_task-probabilisticclassification_run-02_seg-Schaefer2018200Parcels7Networks_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv
```


## Atlases

The merged grey matter masks per subject and the atlases resampled to the individual EPI data are in the directory specified at `--atlases_dir`.

For each subject and each atlas the following data files will be generated

- a `sub-<sub>_space-MNI152NLin2009cAsym_res-2_label-GM_mask.nii.gz`
  Grey matter mask in the dedicated space for a given subject,
  created from merging all the EPI brain masks of a given subject,
  and converges with the grey matter mask of the given space.
- `sub-<sub>_seg-{atlas}{atlas_description}_[dseg|probseg].nii.gz`
  files where the atlas were sampled to `sub-<sub>_space-MNI152NLin2009cAsym_res-2_label-GM_mask.nii.gz`
  for each individual.

- `{atlas}` refers to the name of the atlas used (for example, `Schaefer2018`)
- `{atlas_description}` refers to the sub type of atlas used (for example, `100Parcels7Networks`)

### Example

```
└── sub-1
    └── func
        ├── sub-1_seg-Schaefer2018100Parcels7Networks_dseg.nii.gz
        ├── sub-1_seg-Schaefer2018200Parcels7Networks_dseg.nii.gz
        ├── sub-1_seg-Schaefer2018300Parcels7Networks_dseg.nii.gz
        ├── sub-1_seg-Schaefer2018400Parcels7Networks_dseg.nii.gz
        ├── sub-1_seg-Schaefer2018500Parcels7Networks_dseg.nii.gz
        ├── sub-1_seg-Schaefer2018600Parcels7Networks_dseg.nii.gz
        ├── sub-1_seg-Schaefer2018800Parcels7Networks_dseg.nii.gz
        └── sub-1_space-MNI152NLin2009cAsym_res-2_label-GM_mask.nii.gz
```
