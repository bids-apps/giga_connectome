# What’s new
## 0.8.0.dev

**Released Month Year**

### New

### Fixes

### Enhancements

### Changes

## 0.7.0

**Released November 2026**

### New

- [EHN] Add `--bids-database-path` to set where the PyBIDS database is stored, so the input dataset can be read-only. The path must point to a file named `layout_index.sqlite`. An existing database built for `bids_dir` is reused and never modified; if it cannot be reused, or with `--reindex-bids`, a new database is generated in the output directory. (@htwangtw) [#181](https://github.com/bids-apps/giga_connectome/issues/181)

### Fixes

- [FIX] Set `PYTHONNOUSERSITE=1` in the container so Python packages from the user site directory (`~/.local`) no longer shadow the container environment when running with Apptainer. (@htwangtw) [#278](https://github.com/bids-apps/giga_connectome/issues/278)
- [FIX] Fix `AttributeError: 'NiftiMapsMasker' object has no attribute 'region_ids_'` for probabilistic atlases (DiFuMo). With `--calculate-intranetwork-average-correlation`, probabilistic atlases now skip the average correlation with a warning instead of stopping the run. (@htwangtw)
- [FIX] `--reindex-bids` now rebuilds the PyBIDS database once per run instead of once per participant. (@htwangtw) [#291](https://github.com/bids-apps/giga_connectome/pull/291)
- [FIX] Sort the preset atlas names, so the `--atlas` help text and the Boutiques descriptor no longer change order between runs. (@htwangtw)

### Enhancements

- [DOCS] Add JOSS reference to the citations and use the `README.md` as the documentation landing page. (@htwangtw)[#232](https://github.com/bids-apps/giga_connectome/pull/232)
- [DOCS] Add instructions to run participants in parallel with a shared PyBIDS database. (@htwangtw)

### Changes

- [MAINT] Drop support for Python 3.9 to 3.11. `giga_connectome` now requires Python 3.12 or later, and is tested with Python 3.12 to 3.15. (@Remi-Gau) [#261](https://github.com/bids-apps/giga_connectome/pull/261)
- [MAINT] Remove `--work-dir` (`-w`), deprecated in 0.6.0. Use `--atlases-dir` instead. (@htwangtw)
- [MAINT] Remove the atlas name `Schaefer20187Networks`, deprecated in 0.6.0. Use `Schaefer2018` instead. (@htwangtw)
- [ENH] The PyBIDS database is now stored in `<output_dir>/fmriprep_pybids_db/layout_index.sqlite` by default instead of inside `bids_dir`. Existing datasets will be reindexed once on the first run after upgrading. (@htwangtw) [#181](https://github.com/bids-apps/giga_connectome/issues/181)
- [MAINT] Update the container base image from Python 3.12.3 on Debian 11 (bullseye, end of life) to Python 3.14.10 on Debian 13 (trixie). (@htwangtw)
- [MAINT] Run the container test in CI with a reduced set of DiFuMo (64 and 128 dimensions) and Schaefer2018 (100 and 200 parcels) atlases, so the job fits in the memory of a GitHub runner. The full DiFuMo preset needs about 16 GB of memory for the 1024-dimension atlas. (@htwangtw)
- [MAINT] Update the pinned dependencies of the container, including nilearn 0.10.3 → 0.13.1, numpy 1.26.4 → 2.4.3, scipy 1.12.0 → 1.17.1, pandas 2.2.1 → 3.0.1, scikit-learn 1.4.1 → 1.8.0, pybids 0.15.6 → 0.22.0 and templateflow 0.8.1 → 25.1.2. Time series and connectomes may differ slightly from 0.6.0. (@Remi-Gau) [#263](https://github.com/bids-apps/giga_connectome/pull/263)
- [MAINT] Switch from black and flake8 to ruff for linting and formatting. (@Remi-Gau) [#262](https://github.com/bids-apps/giga_connectome/pull/262)
- [MAINT] Fix the coverage report, which showed 0% since the tests moved out of the package. (@htwangtw) [#290](https://github.com/bids-apps/giga_connectome/pull/290)
- [MAINT] Fix the container test failing on `main` by sharing the test data cache between workflows. (@htwangtw) [#288](https://github.com/bids-apps/giga_connectome/pull/288)


## 0.6.0

**Released May 2025**

### New

- [EHN] Default atlas `Schaefer20187Networks` is renamed to `Schaefer2018`. `Schaefer20187Networks` will be deprecated ub 0.7.0. (@htwangtw)
- [EHN] `--work-dir` is now renamed to `--atlases-dir`. `--work-dir` will be deprecated in 0.7.0. (@htwangtw)
- [EHN] Add details of denoising strategy to the meta data of the time series extraction. (@htwangtw) [#144](https://github.com/bids-apps/giga_connectome/issues/144)
- [DOCS] Add instructions to download atlases packaged in the container for contributors. (@htwangtw)
- [DOCS] Add All Contributors bot. (@htwangtw)

### Fixes

- [FIX] Make sure version docker images matches version of package in the image (@Remi-Gau) [#169](https://github.com/bids-apps/giga_connectome/issues/169)
- [MAINT] Remove recurrsive import. (@htwangtw) [#135](https://github.com/bids-apps/giga_connectome/issues/135)
- [DOCS] Remove `meas` entity in timeseries outputs in the documentation. (@htwangtw) [#136](https://github.com/bids-apps/giga_connectome/issues/136)
- [FIX] Incompatible types in assignment of variable `mask_array` in `giga_connectome/mask.py`. (@htwangtw) [#189](https://github.com/bids-apps/giga_connectome/pull/189)
- [FIX] ICA-AROMA implementation. (@htwangtw) [#211](https://github.com/bids-apps/giga_connectome/issues/211)

### Enhancements

- [DOCS] Improve advance usage example with test data and executable code. (@htwangtw) [#215](https://github.com/bids-apps/giga_connectome/pull/215)
- [DOCS] Clarify fMRIPrep versions supports. (@htwangtw) [#227](https://github.com/bids-apps/giga_connectome/pull/227)

### Changes

- [EHN] Merge `atlas-` and the atlas description `desc-` into one filed `seg-` defined under 'Derivatives-Image data type' in BIDS. (@htwangtw) [#143](https://github.com/bids-apps/giga_connectome/issues/143)
- [EHN] Working directory is now renamed as `atlases/` to reflect on the atlases directory mentioned in BEP017.
- [EHN] Use hyphen instead of underscores for CLI arguments `participant-label` and `smoothing-fwhm`. Underscore variation will be deprecated ub 0.7.0. (@htwangtw) [#190](https://github.com/bids-apps/giga_connectome/pull/190)

## 0.5.0

Released April 2024

### New

- [EHN] Add Harvard-Oxford atlas. (@htwangtw) [#117](https://github.com/bids-apps/giga_connectome/issues/117)
- [DOCS] Improved documentation on using customised configuration files. (@htwangtw)
- [ENH] use logger instead of print statements. (@Remi-Gau)

### Fixes

- [FIX] Bump nilearn version to 0.10.2 to fix issues [#26](https://github.com/bids-apps/giga_connectome/issues/26) and [#27](https://github.com/bids-apps/giga_connectome/issues/27). (@Remi-Gau)

### Enhancements

- [ENH] Reduce the docker image size. (@htwangtw)

### Changes

- [ENH] Make output more BIDS compliant. (@Remi-Gau)
- [MAINT] Pin dependencies for docker build for better reproducibility. (@Remi-Gau)
- [MAINT] Automate docker build and release. (@Remi-Gau, @htwangtw)
- [DOCS] Update the release and post-release procedure (@htwangtw)

## 0.4.0

Released August 2023

### New

- [DOCS] Documentations. What you are reading here. (@htwangtw)
- [EHN] BIDS filter. (@htwangtw)
- [EHN] Calculate average intranetwork correlation (NIAK feature). (@htwangtw)
- [EHN] Add TR as an attribute to time series data. (@htwangtw)
- [MAINT] Fully functional CI and documentations. (@htwangtw)

### Fixes

### Changes

- [EHN] If an output file already exists, it will be overwritten and warning is logged. (@Remi-Gau)
- [EHN] Default atlas is now MIST. (@htwangtw)
- [EHN] When using the `participant` analysis level, the output is one file per subject, rather than one file per scan. (@htwangtw)

## 0.3.0

Released June 2023

### New

- [EHN] expose some preprocessing options: standardization and smoothing. (@htwangtw)
- [EHN] `--version` flag. (@htwangtw)

### Fixes

### Changes

## 0.2.0

Released June 2023

### New

### Fixes

### Changes

- [FIX] Detact different affine matrix from input and use the most common one as group mask resampling target. (@htwangtw)


## 0.1.1

Released May 2023. Hot fix for 0.1.1.

### New

### Fixes
- [FIX] Lock `pybids` and `templateflow` versions as new releases of `pybids` lead to conflicts. (@htwangtw)

### Changes

## 0.1.0

Released May 2023

First working version of the BIDS-app. (@htwangtw)

### New

- [MAINT] Working CI for unit tests (@htwangtw).
- [EHN] Dockerfile (@Hyedryn).

### Fixes

### Changes
