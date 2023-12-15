"""
Process fMRIPrep outputs to timeseries based on denoising strategy.
"""
from __future__ import annotations

import argparse

from giga_connectome import (
    generate_gm_mask_atlas,
    get_denoise_strategy,
    load_atlas_setting,
    run_postprocessing_dataset,
    utils,
)
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
    analysis_level = args.analysis_level
    standardize = utils.parse_standardize_options(args.standardize)
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

    # create subject ts and connectomes
    # refactor the two cases into one

    if analysis_level == "participant":
        for subject in subjects:
            subj_data, fmriprep_bids_layout = utils.get_bids_images(
                [subject], template, bids_dir, args.reindex_bids, bids_filters
            )
            group_mask, resampled_atlases = generate_gm_mask_atlas(
                working_dir, atlas, template, subj_data["mask"]
            )
            connectome_path = output_dir / (
                f"sub-{subject}_atlas-{atlas['name']}"
                f"_desc-{strategy['name']}.h5"
            )
            utils.check_path(connectome_path)

            gc_log.info(f"Generate subject level connectomes: sub-{subject}")

            run_postprocessing_dataset(
                strategy,
                resampled_atlases,
                subj_data["bold"],
                group_mask,
                standardize,
                smoothing_fwhm,
                connectome_path,
                analysis_level,
                calculate_average_correlation,
            )
        return

    # group level
    subj_data, fmriprep_bids_layout = utils.get_bids_images(
        subjects, template, bids_dir, args.reindex_bids, bids_filters
    )
    group_mask, resampled_atlases = generate_gm_mask_atlas(
        working_dir, atlas, template, subj_data["mask"]
    )
    connectome_path = (
        output_dir / f"atlas-{atlas['name']}_desc-{strategy['name']}.h5"
    )
    utils.check_path(connectome_path)

    gc_log.info(connectome_path)
    gc_log.info("Generate subject level connectomes")

    run_postprocessing_dataset(
        strategy,
        resampled_atlases,
        subj_data["bold"],
        group_mask,
        standardize,
        smoothing_fwhm,
        connectome_path,
        analysis_level,
        calculate_average_correlation,
    )
