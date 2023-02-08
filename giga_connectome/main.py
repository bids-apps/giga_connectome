"""
Process fMRIPrep outputs to timeseries based on denoising strategy.
"""
# TODO: the output structutre is not fully bids
from tqdm import tqdm

from bids import BIDSLayout
import nibabel as nib

from giga_connectome import mask
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
    atlas_parameters = mask.load_atlas_setting()[atlas]

    # set file paths
    bids_dir = args.bids_dir
    output_dir = args.output_dir
    working_dir = args.work_dir
    working_dir.mkdir(exist_ok=True, parents=True)
    output_dir.mkdir(exist_ok=True, parents=True)
    connectome_path = output_dir / f"atlas-{atlas}_desc-{strategy_name}.h5"
    if connectome_path.exists():
        raise FileExistsError(
            f"Output file exists. {connectome_path}"
            "Delete or rename the file before running the app "
            "with the same options."
        )
    (working_dir / "groupmasks" / f"tpl-{tpl}").mkdir(
        parents=True, exist_ok=True
    )

    # check the list of subjects to run
    print("Indexing BIDS directory")
    fmriprep_bids_layout = BIDSLayout(
        root=bids_dir,
        database_path=None,  # TODO: look for db in the working directory
        validate=False,
        derivatives=True,
    )
    metadata = get_metadata(fmriprep_bids_layout)
    select_space = metadata["template"] == tpl

    print("Create dataset level masks")
    # no grey matter mask is supplied with MNI152NLin6Asym
    # so we are fixed at using the most common space from
    # fmriprep output
    # TODO: can implement some kinds of caching file found in working dir
    all_masks = metadata.loc[select_space, "mask"]
    group_mask = mask.generate_group_mask(all_masks, "MNI152NLin2009cAsym")
    current_file_name = (
        f"tpl-{tpl}_" "res-dataset_label-GM_desc-group_mask.nii.gz"
    )
    nib.save(
        group_mask,
        (working_dir / "groupmasks" / f"tpl-{tpl}" / current_file_name),
    )

    # dataset level atlas correction
    # TODO: can implement some kinds of caching file found in working dir
    resampled_atlases = []
    for desc in tqdm(atlas_parameters["desc"]):
        parcellation_resampled = mask.resample_atlas2groupmask(
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
        save_path = str(working_dir / "groupmasks" / f"tpl-{tpl}" / filename)
        nib.save(parcellation_resampled, save_path)
        resampled_atlases.append(save_path)

    # filter subjects
    # TODO: separate the mask generation with a flag so advanced user can
    # create different group mask. Currently the group mask is based on the
    # supplied fmriprep derivative. Datasets like ABIDE, is organised by site.
    # User might want a group map across sites
    print("Generate subject level connectomes")

    images = metadata.loc[select_space, "image"]
    run_postprocessing_dataset(
        strategy_parameters[strategy_name],
        resampled_atlases,
        images,
        group_mask,
        connectome_path,
    )


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
