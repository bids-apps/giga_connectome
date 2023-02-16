"""
Process fMRIPrep outputs to timeseries based on denoising strategy.
"""
# TODO: the output structutre is not fully bids

from bids import BIDSLayout
import nibabel as nib
from tqdm import tqdm

from giga_connectome.mask import (
    generate_group_mask,
    resample_atlas2groupmask,
    load_atlas_setting,
)
from giga_connectome.metadata import get_metadata
from giga_connectome.outputs import (
    get_denoise_strategy_parameters,
    run_postprocessing_dataset,
)


def workflow(args):
    print(vars(args))
    # parse denoise strategy
    strategy_parameters = get_denoise_strategy_parameters(
        args.denoise_strategy
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

    # check masks
    group_mask_dir = working_dir / "groupmasks" / f"tpl-{tpl}"
    group_mask, resampled_atlases = None, None
    if group_mask_dir.exists():
        group_mask, resampled_atlases = _check_pregenerated_masks(
            tpl, working_dir, atlas
        )

    group_mask_dir.mkdir(exist_ok=True, parents=True)

    if not group_mask:
        all_masks = metadata.loc[select_space, "mask"]
        group_mask_nii = generate_group_mask(all_masks, "MNI152NLin2009cAsym")
        current_file_name = (
            f"tpl-{tpl}_res-dataset_label-GM_desc-group_mask.nii.gz"
        )
        group_mask = group_mask_dir / current_file_name
        nib.save(group_mask_nii, group_mask)

    if not resampled_atlases:
        resampled_atlases = _resample_atlas_collection(
            tpl, atlas, group_mask_dir, group_mask
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


def _resample_atlas_collection(tpl, atlas, group_mask_dir, group_mask):
    """Resample a atlas collection to group grey matter mask."""
    atlas_parameters = load_atlas_setting()[atlas]
    print("Resample atlas to group grey matter mask.")
    resampled_atlases = []
    for desc in tqdm(atlas_parameters["desc"]):
        parcellation_resampled = resample_atlas2groupmask(
            atlas,
            desc,
            group_mask,
        )
        filename = (
            f"tpl-{tpl}_"
            f"atlas-{atlas_parameters['atlas']}_"
            "res-dataset_"
            f"desc-{desc}_"
            f"{atlas_parameters['type']}.nii.gz"
        )
        save_path = group_mask_dir / filename
        nib.save(parcellation_resampled, save_path)
        resampled_atlases.append(save_path)
    return resampled_atlases


def _check_pregenerated_masks(template, working_dir, atlas):
    """Check if the working directory is populated with needed files."""
    output_dir = working_dir / "groupmasks" / f"tpl-{template}"
    atlas_parameters = load_atlas_setting()[atlas]
    group_mask = (
        output_dir
        / f"tpl-{template}_res-dataset_label-GM_desc-group_mask.nii.gz"
    )
    if not group_mask.exists():
        group_mask = None
    else:
        print(f"Found pregenerated group level grey matter mask: {group_mask}")
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
    all_exist = [file_path.exists() for file_path in resampled_atlases]
    if not all(all_exist):
        resampled_atlases = None
    else:
        print(
            f"Found resampled atlases: {resampled_atlases}. Skipping group "
            "level mask generation step."
        )
    return group_mask, resampled_atlases
