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
    calculate_afc = args.calculate_intranetwork_average_connectivity
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
            connectome_path = utils.check_path(connectome_path, verbose=True)
            print("Generate subject level connectomes")
            run_postprocessing_dataset(
                strategy,
                resampled_atlases,
                subj_data["bold"],
                group_mask,
                standardize,
                smoothing_fwhm,
                connectome_path,
                analysis_level,
                calculate_afc,
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
    connectome_path = utils.check_path(connectome_path, verbose=True)
    print(connectome_path)
    print("Generate subject level connectomes")
    run_postprocessing_dataset(
        strategy,
        resampled_atlases,
        subj_data["bold"],
        group_mask,
        standardize,
        smoothing_fwhm,
        connectome_path,
        analysis_level,
        calculate_afc,
    )
