.. giga_connectome documentation master file, created by
   sphinx-quickstart on Wed Aug 23 14:35:15 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to `giga-connectome`'s documentation!
===========================================

Functional connectivity is a common approach in analysing resting state fMRI data.
The Python tool Nilearn provides utilities to extract and denoise time-series on a parcellation.
Nilearn also has methods to compute functional connectivity.
While Nilearn provides useful methods to generate connectomes,
there is no standalone one stop solution to generate connectomes from fMRIPrep outputs.
`giga-connectome` (a BIDS-app!) combines Nilearn and TemplateFlow to denoise the data, generate timeseries,
and most critically `giga-connectome` generates functional connectomes directly from fMRIPrep outputs.
The workflow comes with several built-in denoising strategies and
there are several choices of atlases (MIST, Schaefer 7 networks, DiFuMo, Harvard-Oxford).
Users can customise their own strategies and atlases using the configuration json files.

`giga-connectome` is tested on fMRIPrep LTS (long-term support) 20.2.x.
Currently, `giga-connectome` fully supports outputs of fMRIPrep LTS.
For fMRIPrep 23.1.0 and later, `giga-connectome` does not support ICA-AROMA denoising,
as the strategy is removed from the fMRIPrep workflow.

.. toctree::
   :maxdepth: 1
   :caption: Contents

   installation.md
   usage.md
   workflow.md
   outputs.md

.. toctree::
   :maxdepth: 1
   :caption: Contribution and maintenance

   contributing.md
   api.rst
   changes.md

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
