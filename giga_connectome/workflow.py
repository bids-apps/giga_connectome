"""
Process fMRIPrep outputs to timeseries based on denoising strategy.
"""

from __future__ import annotations

import argparse

from giga_connectome.mask import generate_gm_mask_atlas
from giga_connectome.atlas import load_atlas_setting
from giga_connectome.denoise import get_denoise_strategy
from giga_connectome import methods, utils
from giga_connectome.postprocess import run_postprocessing_dataset

from giga_connectome.denoise import is_ica_aroma
from giga_connectome.logger import gc_logger

gc_log = gc_logger()


def set_verbosity(verbosity: int | list[int]) -> None:
    if isinstance(verbosity, list):
        verbosity = verbosity[0]
    if verbosity == 0:
        gc_log.setLevel("ERROR")
    elif verbosity == 1:
        gc_log.setLevel("WARNING")
    elif verbosity == 2:
        gc_log.setLevel("INFO")
    elif verbosity == 3:
        gc_log.setLevel("DEBUG")


def workflow(args: argparse.Namespace) -> None:
    gc_log.info(vars(args))

    # set file paths
    bids_dir = args.bids_dir
    output_dir = args.output_dir
    working_dir = args.work_dir
    standardize = True  # always standardising the time series
    smoothing_fwhm = args.smoothing_fwhm
    calculate_average_correlation = (
        args.calculate_intranetwork_average_correlation
    )
    bids_filters = utils.parse_bids_filter(args.bids_filter_file)

    subjects = utils.get_subject_lists(args.participant_label, bids_dir)
    strategy = get_denoise_strategy(args.denoise_strategy)

    atlas = load_atlas_setting(args.atlas)

    set_verbosity(args.verbosity)

    # check output path
    output_dir.mkdir(parents=True, exist_ok=True)
    working_dir.mkdir(parents=True, exist_ok=True)

    # get template information; currently we only support the fmriprep defaults
    template = (
        "MNI152NLin6Asym" if is_ica_aroma(strategy) else "MNI152NLin2009cAsym"
    )

    gc_log.info(f"Indexing BIDS directory:\n\t{bids_dir}")

    utils.create_ds_description(output_dir)
    utils.create_sidecar(output_dir / "meas-PearsonCorrelation_relmat.json")
    methods.generate_method_section(
        output_dir=output_dir,
        atlas=atlas["name"],
        smoothing_fwhm=smoothing_fwhm,
        standardize="zscore",
        strategy=args.denoise_strategy,
        mni_space=template,
        average_correlation=calculate_average_correlation,
    )

    for subject in subjects:
        subj_data, _ = utils.get_bids_images(
            [subject], template, bids_dir, args.reindex_bids, bids_filters
        )
        group_mask, resampled_atlases = generate_gm_mask_atlas(
            working_dir, atlas, template, subj_data["mask"]
        )

        gc_log.info(f"Generate subject level connectomes: sub-{subject}")

        run_postprocessing_dataset(
            strategy,
            atlas,
            resampled_atlases,
            subj_data["bold"],
            group_mask,
            standardize,
            smoothing_fwhm,
            output_dir,
            calculate_average_correlation,
        )
    return
