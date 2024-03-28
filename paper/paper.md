---
title: 'Giga Connectome: a BIDS-app for time series and functional connectome extraction'
tags:
  - BIDS
  - Python
  - fMRI
  - functional connectivity
authors:
  - name: Hao-Ting Wang
    corresponding: true
    orcid: 0000-0003-4078-2038
    affiliation: 1 # (Multiple affiliations must be quoted)
  - name: Rémi Gau
  - name: Natasha Clarke
    affiliation: 1
  - name: Quentin Dessain
  - name: Pierre Bellec
    orcid: 0000-0002-9111-0699
    affiliation: 1
affiliations:
- name: Centre de Recherche de l'Institut Universitaire de Gériatrie de Montréal, Université de Montréal, Montréal, QC, Canada
  index: 1
date: XX April 2024
bibliography: paper.bib
---

# Summary

Researchers perform two steps before Functional magnetic resonance imaging (fMRI) data analysis:
standardised preprocessing and customised denoising.
`fMRIPrep` [@fmriprep; RRID:SCR_016216],
a popular software in the neuroimaging community, is a common choice for preprocessing.
`fMRIPrep` performs minimal preprocessing, leaving a few steps for the end user: smoothing, denoising, and standardisation.
The present software, `giga-connectome`,
is a Brain Imaging Data Structure [BIDS; @bids]
compliant container image that aims to perform these steps as well as extract time series signals and generate connectomes for machine learning applications.
All these steps are implemented with functions from `nilearn` [@Nilearn; RRID:SCR_001362],
a python library for machine learning in neuroimaging.

The tool performs smoothing, denoising, and standardisation on voxel level data.
Smoothing is implemented with a 5mm full width at half maximum kernel and the user can change the kernel size based on the voxel size of their fMRI data.
For the denoising step, we built the workflow closely aligned with the design choice of fmriprep [@wang_continuous_2024]
and worked with the fmriprep developers while implementing a key Application Programming Interface (API),
`load_confounds`, implemented in the software library `nilearn`.
The tool provides some preset strategies based on wang et al and the current long-term support release `fMRIPrep`.
Users can implement their own strategy using configuration files.
The denoising strategy configuration will allow them to directly interact with the `load_confounds` API.
The details of the process can be found in the [user documentation](https://giga-connectome.readthedocs.io/en/stable/workflow.html).
Finally the data is standardised as z-scores.

The atlas for time series extraction was retrieved through `templateflow` [@templateflow],
a brain template and atlas naming system with a Python API.
The container image provides some default atlases
(Harvard-Oxford [@makris_decreased_2006; @goldstein_hypothalamic_2007; @frazier_structural_2005; @desikan_automated_2006],
Schaefer [@schaefer_local-global_2018],
MIST [@urchs_mist_2019],
and DiFuMo [@dadi_fine-grain_2020]) that are already available in the `templateflow` repository.
Customised atlases will have to be formatted in `templateflow` convention and supplied using a configuration file.
We aim to include more default atlases when they are included in the templateflow repository.

The time series extraction is implemented with nilearn niftilabelsmasker and niftimapsmasker objects.
The generated time series are used to construct connectomes calculated as Pearson’s correlation with nilearn object connectivity measure.

Finally the saved time series and connectomes follow the format of
[BIDS-connectome specification](https://bids.neuroimaging.io/bep017).
Users can follow the specification to interpret and retrieve the relevant results.
The coverage of the atlas is also included as a html visual report, provided by nilearn masker for users to examine the quality of the atlas coverage.
More information about the usage, workflow, and outputs can be found on the
[official documentation](https://giga-connectome.readthedocs.io/en/latest/).


# Statement of need

Giga-connectome is created for large scale deployment on multiple fMRIPrep preprocessed neuroimaging datasets.
We aimed to create a tool that is lightweight in terms of code base complexity, software dependencies, and command line interface (CLI).
The current software follows the BIDS-apps API [@bidsapp] and is the first of its kind that creates outputs in the BIDS-connectome.
Both users and developers would benefit from the detailed definition of BIDS-apps API and BIDS-connectome for shared usage documentation and development guidelines.
The key dependencies of the software are python clients of BIDS or BIDS adjacent projects (pyBIDS and templateflow python client) and nilearn,
which is an open source library of high quality and with a clear development cycle for future maintenance.
We used configuration files to structure the choice of denoising strategies and brain atlas to avoid crowding the CLI and ensure the choices of the user are traceable.

We aim to provide a lightweight alternative to other existing post-fMRIPrep processing software such as XCP-D [@xcp-d]
and HALFPipe [@HALFpipe],
or preprocessing software with fMRIPrep support such as C-PAC [@cpac]
and CONN [@conn ;RRID:SCR_009550].
These tools  provide more flexibility and options for denoising and more types of downstream feature extraction for a wider range of fMRI analysis.
Giga connectome was intentionally designed with a narrow scope for quick deployment and the ease for machine learning researchers to adopt.
We hope this modular implementation can eventually be included as part of these existing workflows so all fMRIPrep outputs can share a time series and connectome extraction tool that’s minimal and streamlined.
Furthermore, this lean design choice aims to reduce the barrier to learning the code base and the ease of on-boarding new contributors.
We hope this choice will invite more users to contribute to the tool and benefit from the open source neuroimaging community.

Giga connectome has already been deployed on multiple large neuroimaging datasets such as
ABIDE [@ABIDE],
ADHD200 [@adhd200],
UKBiobank [@ukbiobank],
and more.
The generated time series and connectomes have been included in a registered report [@clarke_2024],
and various work under preparation in the SIMEXP lab and CNeuromod project.
The data processing scripts using giga connectome can be found
[here](https://github.com/Hyedryn/ukbb-scripts/tree/dev) for UK Biobank
and [this repository](https://github.com/SIMEXP/giga_preprocess2) for the other datasets.

# Acknowledgement

The project was supported by the following fundings:
Digital Alliance Canada Resource Allocation Competition (RAC 1827 and RAC 4455) to PB,
Institut de Valorisation des Données projets de recherche stratégiques
(IVADO PFR3) to PB,
and Canadian Consortium on Neurodegeneration in Aging
(CCNA; team 9 "discovering new biomarkers") to PB,
the Courtois Foundation to PB,
and Institut national de recherche en sciences et technologies du numérique
(INRIA; Programme Équipes Associées - NeuroMind Team DRI-012229) to PB.

HTW is supported by IVADO postdoc fellowship.
NC is supported by IVADO postdoc fellowship.
QD is a research fellow of the Fonds de la Recherche Scientifique - FNRS of Belgium.
RG is supported by funding from the Chan Zuckerberg Initiative.
PB was funded by Fonds de Recherche du Québec - Santé.

# Reference
