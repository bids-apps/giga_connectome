"""
Process fMRIPrep outputs to timeseries based on denoising strategy.
"""
from giga_connectome import (
    generate_gm_mask_atlas,
    load_atlas_setting,
    run_postprocessing_dataset,
    get_denoise_strategy,
)

from giga_connectome.denoise import is_ica_aroma
from giga_connectome import utils


def workflow(args):
    print(vars(args))
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

    # check output path
    output_dir.mkdir(parents=True, exist_ok=True)
    working_dir.mkdir(parents=True, exist_ok=True)

    # get template information; currently we only support the fmriprep defaults
    template = (
        "MNI152NLin6Asym" if is_ica_aroma(strategy) else "MNI152NLin2009cAsym"
    )
    print("Indexing BIDS directory")

    utils.create_ds_description(output_dir)
    utils.create_sidecar(
        output_dir
        / f"meas-PearsonCorrelation_desc-{args.denoise_strategy}_relmat.json"
    )

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

            print("Generate subject level connectomes")
            run_postprocessing_dataset(
                strategy,
                resampled_atlases,
                subj_data["bold"],
                group_mask,
                standardize,
                smoothing_fwhm,
                output_dir,
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
    print("Generate subject level connectomes")
    run_postprocessing_dataset(
        strategy,
        resampled_atlases,
        subj_data["bold"],
        group_mask,
        standardize,
        smoothing_fwhm,
        output_dir,
        analysis_level,
        calculate_average_correlation,
    )
