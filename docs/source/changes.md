# What’s new

## 0.5.1.dev

**Released MONTH YEAR**

### New

### Fixes

### Enhancements

### Changes

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
