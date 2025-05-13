# What’s new

## 0.6.0

**Released May 2025**

### New

- [EHN] Default atlas `Schaefer20187Networks` is renamed to `Schaefer2018`. `Schaefer20187Networks` will be deprecated ub 0.7.0. (@htwangtw)
- [EHN] `--work-dir` is now renamed to `--atlases-dir`. `--work-dir` will be deprecated ub 0.7.0. (@htwangtw)
- [EHN] Add details of denoising strategy to the meta data of the time series extraction. (@htwangtw) [#144](https://github.com/bids-apps/giga_connectome/issues/144)
- [DOCS] Add instructions to download atlases packaged in the container for contributors. (@htwangtw)
- [DOCS] Add All Contributors bot. (@htwangtw)

### Fixes

- [FIX] Make sure version docker images matches version of package in the image (@Remi-Gau) [#169](https://github.com/bids-apps/giga_connectome/issues/169)
- [MAINT] Remove recurrsive import. (@htwangtw) [#135](https://github.com/bids-apps/giga_connectome/issues/135)
- [DOCS] Remove`meas` entity in timeseries outputs in the documentation. (@htwangtw) [#136](https://github.com/bids-apps/giga_connectome/issues/136)
- [FIX] Incompatible types in assignment of variable `mask_array` in `giga_connectome/mask.py`. (@htwangtw) [#189](https://github.com/bids-apps/giga_connectome/pull/189)
- [FIX] ICA-AROMA implementation. (@htwangtw) [#211](https://github.com/bids-apps/giga_connectome/issues/211)

### Enhancements

- [DOCS] Improve advance usage example with test data and executable code. (@htwangtw) [#189](https://github.com/bids-apps/giga_connectome/pull/215)

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
