[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/bids-apps/giga_connectome/branch/main/graph/badge.svg?token=P4EGV7NKZ8)](https://codecov.io/gh/bids-apps/giga_connectome)
[![.github/workflows/test.yml](https://github.com/bids-apps/giga_connectome/actions/workflows/test.yml/badge.svg)](https://github.com/bids-apps/giga_connectome/actions/workflows/test.yml)
[![pre-commit](https://github.com/bids-apps/giga_connectome/actions/workflows/run_precommit.yml/badge.svg)](https://github.com/bids-apps/giga_connectome/actions/workflows/run_precommit.yml)
[![Documentation Status](https://readthedocs.org/projects/giga-connectome/badge/?version=stable)](https://giga-connectome.readthedocs.io/en/latest/?badge=stable)
![https://github.com/psf/black](https://img.shields.io/badge/code%20style-black-000000.svg)
![](https://img.shields.io/docker/pulls/bids/giga_connectome)

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

## Quick start

Pull from `Dockerhub` (Recommended)

```bash
docker pull bids/giga_connectome:latest
docker run -ti --rm --read-only bids/giga_connectome --help
```

If you want to get the bleeding-edge version of the app,
pull the `unstable` version.

```bash
docker pull bids/giga_connectome:unstable
```

## How to report errors

Please use the [GitHub issue](https://github.com/bids-apps/giga_connectome/issues) to report errors.
Check out the open issues first to see if we're already working on it.
If not, [open up a new issue](https://github.com/bids-apps/giga_connectome/issues/new)!

## How to contribute

You can review open [issues]((https://github.com/bids-apps/giga_connectome/issues)) that we are looking for help with.
If you submit a new pull request please be as detailed as possible in your comments.

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
