"""
Process fMRIPrep outputs to timeseries based on denoising strategy.
"""
# TODO: the output structutre is not fully bids
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
    bids_dir = args.bids_dir
    output_dir = args.output_dir
    working_dir = args.work_dir
    working_dir.mkdir(exist_ok=True, parents=True)
    output_dir.mkdir(exist_ok=True, parents=True)

    # parse denoise strategy
    strategy_parameters = _parse_strategy(
        args.denoise_strategy, args.global_signal
    )
    strategy_name = list(strategy_parameters.keys())[0]
    # template
    tpl = "MNI152NLin2009cAsym"
    if args.denoise_strategy == "icaaroma":
        tpl = "MNI152NLin6Asym"

    # atlas
    atlas = args.atlas
    atlas_parameters = mask.load_atlas_setting()[atlas]

    # check the list of subjects to run
    print("Indexing BIDS directory")
    fmriprep_bids_layout = BIDSLayout(
        root=bids_dir,
        database_path=None,
        validate=False,
        derivatives=True,
    )
    metadata = get_metadata(fmriprep_bids_layout)

    print("Create dataset level masks")
    (working_dir / "groupmasks" / f"tpl-{tpl}").mkdir(
        parents=True, exist_ok=True
    )
    epis = metadata[metadata["template"] == tpl]
    all_masks = epis["mask"].tolist()

    # no grey matter mask is supplied with MNI152NLin6Asym
    # so we are fixed at using the most common space from
    # fmriprep output
    group_mask = mask.generate_group_mask(all_masks, "MNI152NLin2009cAsym")

    current_file_name = (
        f"tpl-{tpl}_" "res-dataset_label-GM_desc-group_mask.nii.gz"
    )
    nib.save(
        group_mask,
        (working_dir / "groupmasks" / f"tpl-{tpl}" / current_file_name),
    )

    # dataset level atlas correction
    resampled_atlases = []
    for desc in atlas_parameters["desc"]:
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
    print("Generate subject level connectomes")
    select_space = metadata["template"] == tpl
    images = metadata.loc[select_space, "image"]
    output_path = output_dir / f"atlas-{atlas}_desc-{strategy_name}.h5"
    run_postprocessing_dataset(
        strategy_parameters[strategy_name],
        resampled_atlases,
        images,
        group_mask,
        output_path,
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
