"""
Process fMRIPrep outputs to timeseries based on denoising strategy.
"""
# TODO: the output structutre is not fully bids

from bids import BIDSLayout

from giga_connectome.mask import create_group_masks_atlas, load_atlas_setting
from giga_connectome.metadata import get_metadata
from giga_connectome.outputs import (
    get_denoise_strategy_parameters,
    run_postprocessing_dataset,
)


def main(args):
    print(vars(args))
    # parse denoise strategy
    strategy_parameters = _parse_strategy(
        args.denoise_strategy, args.global_signal
    )
    strategy_name = list(strategy_parameters.keys())[0]
    # template
    tpl = (
        "MNI152NLin2009cAsym"
        if args.denoise_strategy != "icaaroma"
        else "MNI152NLin6Asym"
    )

    # atlas
    atlas = args.atlas

    # set file paths
    bids_dir = args.bids_dir
    output_dir = args.output_dir
    working_dir = args.work_dir

    # check output
    output_dir.mkdir(exist_ok=True, parents=True)
    connectome_path = output_dir / f"atlas-{atlas}_desc-{strategy_name}.h5"
    if connectome_path.exists():
        raise FileExistsError(
            f"Output file exists. {connectome_path}"
            "Delete or rename the file before running the app "
            "with the same options."
        )

    # check masks
    group_mask_dir = working_dir / "groupmasks" / f"tpl-{tpl}"
    group_mask, resampled_atlases = None, None
    if group_mask_dir.exists():
        group_mask, resampled_atlases = _check_pregenerated_masks(
            tpl, working_dir, atlas
        )
    group_mask_dir.mkdir(exist_ok=True, parents=True)

    # check the list of subjects to run
    print("Indexing BIDS directory")
    fmriprep_bids_layout = BIDSLayout(
        root=bids_dir,
        database_path=working_dir,
        validate=False,
        derivatives=True,
    )
    metadata = get_metadata(fmriprep_bids_layout)
    select_space = metadata["template"] == tpl

    if not group_mask:
        print(
            "Create dataset level masks with all EPI masks from the "
            "current fMRIPrep derivative."
        )
        all_masks = metadata.loc[select_space, "mask"]
        group_mask, resampled_atlases = create_group_masks_atlas(
            all_masks, tpl, atlas, group_mask_dir
        )

    # filter subjects
    print("Generate subject level connectomes")
    images = metadata.loc[select_space, "image"]
    run_postprocessing_dataset(
        strategy_parameters[strategy_name],
        resampled_atlases,
        images,
        group_mask,
        connectome_path,
    )


def _check_pregenerated_masks(template, working_dir, atlas):
    """Check if the working directory is populated with needed files."""
    output_dir = working_dir / "groupmasks" / f"tpl-{template}"
    atlas_parameters = load_atlas_setting()[atlas]
    group_mask = (
        output_dir
        / f"tpl-{template}_res-dataset_label-GM_desc-group_mask.nii.gz"
    )
    resampled_atlases = []
    for desc in atlas_parameters["desc"]:
        filename = (
            f"tpl-{template}_"
            f"atlas-{atlas_parameters['atlas']}_"
            "res-dataset_"
            f"desc-{desc}_"
            f"{atlas_parameters['type']}.nii.gz"
        )
        resampled_atlases.append(output_dir / filename)
    all_exist = [
        file_path.exists() for file_path in resampled_atlases + [group_mask]
    ]
    if not all(all_exist):
        raise FileNotFoundError(
            "Not all resampled mask and/or atlas needed for the current "
            "workflow needed for the current workflow are present in "
            f"{working_dir}. Please regenerate the missing files, or "
            "point to a clean working directory."
        )
    print(
        f"Found pregenerated group level grey matter mask: {group_mask}"
        f"and resampled atlases: {resampled_atlases}. Skipping group level"
        "mask generation step."
    )
    return group_mask, resampled_atlases


def _parse_strategy(denoise_strategy, global_signal):
    if global_signal:
        if denoise_strategy in ["simple", "scrubbing.2", "scrubbing.5"]:
            denoise_strategy += "+gsr"
        else:
            UserWarning(
                f'Strategy "{denoise_strategy}" doesn\'t allow '
                "additional global signal regressor. "
                "Ignore this flag."
            )
    return get_denoise_strategy_parameters(denoise_strategy)
