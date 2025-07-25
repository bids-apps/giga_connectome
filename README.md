[![DOI](https://joss.theoj.org/papers/10.21105/joss.07061/status.svg)](https://doi.org/10.21105/joss.07061)
[![All Contributors](https://img.shields.io/github/all-contributors/bids-apps/giga_connectome?color=ee8449&style=flat)](#contributors)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![codecov](https://codecov.io/gh/bids-apps/giga_connectome/branch/main/graph/badge.svg?token=P4EGV7NKZ8)](https://codecov.io/gh/bids-apps/giga_connectome)
[![.github/workflows/test.yml](https://github.com/bids-apps/giga_connectome/actions/workflows/test.yml/badge.svg)](https://github.com/bids-apps/giga_connectome/actions/workflows/test.yml)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/bids-apps/giga_connectome/main.svg)](https://results.pre-commit.ci/latest/github/bids-apps/giga_connectome/main)
[![Documentation Status](https://readthedocs.org/projects/giga-connectome/badge/?version=stable)](https://giga-connectome.readthedocs.io/en/latest/?badge=stable)
![https://github.com/psf/black](https://img.shields.io/badge/code%20style-black-000000.svg)
[![Docker pulls](https://img.shields.io/docker/pulls/bids/giga_connectome)](https://hub.docker.com/r/bids/giga_connectome/tags)

# giga-connectome

This is a BIDS-App to extract signal from a parcellation with `nilearn`,
typically useful in a context of resting-state data processing.

You can read our [JOSS paper](https://doi.org/10.21105/joss.07061) for the background of the project and the details of implementations.

## Description

Functional connectivity is a common approach in analysing resting state fMRI data.
The Python tool `Nilearn` provides utilities to extract and denoise time-series on a parcellation.
`Nilearn` also has methods to compute functional connectivity.
While `Nilearn` provides useful methods to generate connectomes,
there is no standalone one stop solution to generate connectomes from `fMRIPrep` outputs.
`giga-connectome` (a BIDS-app!) combines `Nilearn` and `TemplateFlow` to denoise the data, generate timeseries,
and most critically `giga-connectome` generates functional connectomes directly from `fMRIPrep` outputs.
The workflow comes with several built-in denoising strategies and
there are several choices of atlases (MIST, Schaefer 7 networks, DiFuMo, Harvard-Oxford).
Users can customise their own strategies and atlases using the configuration json files.


## Supported `fMRIPrep` versions

`giga-connectome` fully supports outputs of fMRIPrep LTS (long-term support) 20.2.x.

For `fMRIPrep` 23.1.0 and later, `giga-connectome` does not support ICA-AROMA denoising,
as the strategy is removed from the `fMRIPrep` workflow.

## Quick start

Pull from `Dockerhub` (Recommended)

```bash
docker pull bids/giga_connectome:latest
docker run -ti --rm bids/giga_connectome --help
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
If you have any question related how to create a pull request, you can check our [documentation for contributors](https://giga-connectome.readthedocs.io/en/latest/contributing.html).

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://wanghaoting.com/"><img src="https://avatars.githubusercontent.com/u/13743617?v=4?s=100" width="100px;" alt="Hao-Ting Wang"/><br /><sub><b>Hao-Ting Wang</b></sub></a><br /><a href="#ideas-htwangtw" title="Ideas, Planning, & Feedback">🤔</a> <a href="#research-htwangtw" title="Research">🔬</a> <a href="#code-htwangtw" title="Code">💻</a> <a href="#test-htwangtw" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Hyedryn"><img src="https://avatars.githubusercontent.com/u/5383293?v=4?s=100" width="100px;" alt="Quentin Dessain"/><br /><sub><b>Quentin Dessain</b></sub></a><br /><a href="#userTesting-Hyedryn" title="User Testing">📓</a> <a href="#platform-Hyedryn" title="Packaging/porting to new platform">📦</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/clarkenj"><img src="https://avatars.githubusercontent.com/u/57987005?v=4?s=100" width="100px;" alt="Natasha Clarke"/><br /><sub><b>Natasha Clarke</b></sub></a><br /><a href="#userTesting-clarkenj" title="User Testing">📓</a> <a href="#example-clarkenj" title="Examples">💡</a> <a href="#bug-clarkenj" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://remi-gau.github.io/"><img src="https://avatars.githubusercontent.com/u/6961185?v=4?s=100" width="100px;" alt="Remi Gau"/><br /><sub><b>Remi Gau</b></sub></a><br /><a href="#infra-Remi-Gau" title="Infrastructure (Hosting, Build-Tools, etc)">🚇</a> <a href="#maintenance-Remi-Gau" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://simexp.github.io"><img src="https://avatars.githubusercontent.com/u/1670887?v=4?s=100" width="100px;" alt="Lune Bellec"/><br /><sub><b>Lune Bellec</b></sub></a><br /><a href="#ideas-pbellec" title="Ideas, Planning, & Feedback">🤔</a> <a href="#financial-pbellec" title="Financial">💵</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/shnizzedy"><img src="https://avatars.githubusercontent.com/u/5974438?v=4?s=100" width="100px;" alt="Jon Cluce"/><br /><sub><b>Jon Cluce</b></sub></a><br /><a href="#bug-shnizzedy" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/emullier"><img src="https://avatars.githubusercontent.com/u/43587002?v=4?s=100" width="100px;" alt="Emeline Mullier"/><br /><sub><b>Emeline Mullier</b></sub></a><br /><a href="#bug-emullier" title="Bug reports">🐛</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://jdkent.github.io/"><img src="https://avatars.githubusercontent.com/u/12564882?v=4?s=100" width="100px;" alt="James Kent"/><br /><sub><b>James Kent</b></sub></a><br /><a href="#bug-jdkent" title="Bug reports">🐛</a> <a href="#doc-jdkent" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://marcel.stimberg.info"><img src="https://avatars.githubusercontent.com/u/1381982?v=4?s=100" width="100px;" alt="Marcel Stimberg"/><br /><sub><b>Marcel Stimberg</b></sub></a><br /><a href="#userTesting-mstimberg" title="User Testing">📓</a> <a href="#doc-mstimberg" title="Documentation">📖</a> <a href="#bug-mstimberg" title="Bug reports">🐛</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

## Acknowledgements

Please cite the following paper if you are using `giga-connectome` in your work:
```bibtex
@article{Wang2025,
    doi = {10.21105/joss.07061},
    url = {https://doi.org/10.21105/joss.07061},
    year = {2025}, publisher = {The Open Journal},
    volume = {10},
    number = {110},
    pages = {7061},
    author = {Hao-Ting Wang and Rémi Gau and Natasha Clarke and Quentin Dessain and Lune Bellec},
    title = {Giga Connectome: a BIDS-app for time series and functional connectome extraction},
    journal = {Journal of Open Source Software}
}
```

`giga-connectome` uses `nilearn` under the hood,
hence please consider cite `nilearn` using the Zenodo DOI:

```bibtex
@software{Nilearn,
    author = {Nilearn contributors},
    license = {BSD-4-Clause},
    title = {{nilearn}},
    url = {https://github.com/nilearn/nilearn},
    doi = {https://doi.org/10.5281/zenodo.8397156}
}
```
Nilearn’s Research Resource Identifier (RRID) is: [RRID:SCR_001362][]

We acknowledge all the [nilearn developers][]
as well as the [BIDS-Apps team][]

This is a Python project packaged according to [Contemporary Python Packaging - 2023][].

[Contemporary Python Packaging - 2023]: https://effigies.gitlab.io/posts/python-packaging-2023/
[RRID:SCR_001362]: https://rrid.site/data/record/nlx_144509-1/SCR_001362/resolver?q=nilearn&l=nilearn&i=rrid:scr_001362
[nilearn developers]: https://github.com/nilearn/nilearn/graphs/contributors
[BIDS-Apps team]:https://github.com/orgs/BIDS-Apps/people
