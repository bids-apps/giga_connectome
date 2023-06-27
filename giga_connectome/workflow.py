"""
Process fMRIPrep outputs to timeseries based on denoising strategy.
"""
from pathlib import Path
from bids import BIDSLayout
from bids.layout import Query
import nibabel as nib

from giga_connectome.mask import (
    generate_group_mask,
    resample_atlas_collection,
    load_atlas_setting,
)
from giga_connectome.outputs import (
    get_denoise_strategy_parameters,
    run_postprocessing_dataset,
)
from giga_connectome import utils


def workflow(args):
    print(vars(args))
    # set file paths
    bids_dir = args.bids_dir
    output_dir = args.output_dir
    working_dir = args.work_dir
    analysis_level = args.analysis_level
    standardize = _parse_standardize_options(args.standardize)
    smoothing_fwhm = args.smoothing_fwhm

    subjects = utils.get_subject_lists(args.participant_label, bids_dir)
    strategy = get_denoise_strategy_parameters(args.denoise_strategy)
    atlas = load_atlas_setting(args.atlas)

    # check output path
    output_dir.mkdir(parents=True, exist_ok=True)
    working_dir.mkdir(parents=True, exist_ok=True)

    # get template information; currently we only support the fmriprep defaults
    tpl = (
        "MNI152NLin6Asym" if _is_ica_aroma(strategy) else "MNI152NLin2009cAsym"
    )
    print("Indexing BIDS directory")
    # BIDS filter
    # https://github.com/nipreps/fmriprep/blob/689ad26811cfb18771fdb8d7dc208fe24d27e65c/fmriprep/cli/parser.py#L72
    fmriprep_bids_layout = BIDSLayout(
        root=bids_dir,
        database_path=bids_dir,
        validate=False,
        derivatives=True,
    )
    image_filter = {
        "subject": subjects,
        "space": tpl,
        "task": Query.ANY,
        "desc": "preproc",
        "suffix": "bold",
        "extension": "nii.gz",
    }

    images = fmriprep_bids_layout.get(**image_filter, return_type="file")

    group_mask, resampled_atlases = _generate_gm_mask_atlas(
        working_dir, atlas, tpl, fmriprep_bids_layout, subjects
    )

    # create subject ts and connectomes
    if analysis_level == "group":
        connectome_path = (
            output_dir / f"atlas-{atlas['name']}_desc-{strategy['name']}.h5"
        )
        connectome_path = _check_path(connectome_path, verbose=True)
        print("Generate subject level connectomes")
        run_postprocessing_dataset(
            strategy,
            resampled_atlases,
            images,
            group_mask,
            standardize,
            smoothing_fwhm,
            connectome_path,
            analysis_level,
        )
    elif analysis_level == "participant":
        for img in images:
            subject, session, specifier = utils.parse_bids_name(img)
            basename = f"{subject}_{session}_{specifier}_space-{tpl}"
            connectome_path = output_dir / (
                f"{basename}_atlas-{atlas['name']}"
                f"_desc-{strategy['name']}.h5"
            )
            connectome_path = _check_path(connectome_path, verbose=True)
            print("Generate subject level connectomes")
            run_postprocessing_dataset(
                strategy,
                resampled_atlases,
                [img],
                group_mask,
                standardize,
                smoothing_fwhm,
                connectome_path,
                analysis_level,
            )


def _parse_standardize_options(standardize):
    if standardize not in ["zscore", "psc"]:
        raise ValueError(f"{standardize} is no valid standardize strategy.")
    if standardize == "psc":
        return standardize
    else:
        return True


def _generate_gm_mask_atlas(
    working_dir, atlas, template, fmriprep_bids_layout, subjects
):
    # check masks; isolate this part and make sure to make it a validate
    # templateflow template with a config file
    mask_filter = {
        "subject": subjects,
        "space": template,
        "task": Query.ANY,
        "suffix": "mask",
        "extension": "nii.gz",
    }
    group_mask_dir = working_dir / "groupmasks" / f"tpl-{template}"
    group_mask_dir.mkdir(exist_ok=True, parents=True)

    group_mask, resampled_atlases = None, None
    if group_mask_dir.exists():
        group_mask, resampled_atlases = _check_pregenerated_masks(
            template, working_dir, atlas
        )

    if not group_mask:
        masks = fmriprep_bids_layout.get(**mask_filter, return_type="file")
        # grey matter group mask is only supplied in MNI152NLin2009c(A)sym
        group_mask_nii = generate_group_mask(masks, "MNI152NLin2009cAsym")
        current_file_name = (
            f"tpl-{template}_res-dataset_label-GM_desc-group_mask.nii.gz"
        )
        group_mask = group_mask_dir / current_file_name
        nib.save(group_mask_nii, group_mask)

    if not resampled_atlases:
        resampled_atlases = resample_atlas_collection(
            template, atlas, group_mask_dir, group_mask
        )

    return group_mask, resampled_atlases


def _check_pregenerated_masks(template, working_dir, atlas):
    """Check if the working directory is populated with needed files."""
    output_dir = working_dir / "groupmasks" / f"tpl-{template}"
    group_mask = (
        output_dir
        / f"tpl-{template}_res-dataset_label-GM_desc-group_mask.nii.gz"
    )
    if not group_mask.exists():
        group_mask = None
    else:
        print(f"Found pregenerated group level grey matter mask: {group_mask}")

    # atlas
    resampled_atlases = []
    for desc in atlas["file_paths"]:
        filename = (
            f"tpl-{template}_"
            f"atlas-{atlas['name']}_"
            "res-dataset_"
            f"desc-{desc}_"
            f"{atlas['type']}.nii.gz"
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


def _is_ica_aroma(strategy):
    """Check if the current strategy is ICA AROMA."""
    strategy_preset = strategy["parameters"].get("denoise_strategy", False)
    strategy_user_define = strategy["parameters"].get("strategy", False)
    if strategy_preset or strategy_user_define:
        return (
            strategy_preset == "ica_aroma"
            if strategy_preset
            else "ica_aroma" in strategy_user_define
        )
    else:
        raise ValueError(f"Invalid input dictionary. {strategy['parameters']}")


def _check_path(path: Path, verbose=True):
    """Check if given path (file or dir) already exists, and if so returns a
    new path with _<n> appended (n being the number of paths with the same name
    that exist already).
    """
    path = path.resolve()
    ext = path.suffix
    path_parent = path.parent

    if path.exists():
        similar_paths = [
            str(p).replace(ext, "")
            for p in path_parent.glob(f"{path.stem}_*{ext}")
        ]
        existing_numbers = [
            int(p.split("_")[-1])
            for p in similar_paths
            if p.split("_")[-1].isdigit()
        ]
        n = str(max(existing_numbers) + 1) if existing_numbers else "1"
        path = path_parent / f"{path.stem}_{n}{ext}"
        if verbose:
            print(f"Specified path already exists, using {path} instead.")
    return path
