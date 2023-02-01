"""
Process fMRIPrep outputs to timeseries based on denoising strategy.
"""
# TODO: the output structutre is not fully bids
from pathlib import Path

from bids import BIDSLayout
import nibabel as nib

from giga_connectome.metadata import get_metadata
from giga_connectome import mask
from nilearn.maskers import NiftiMasker, NiftiLabelsMasker, NiftiMapsMasker
from nilearn.interfaces.fmriprep import load_confounds_strategy
from nilearn.connectome import ConnectivityMeasure

from giga_connectome.denoise import get_denoise_strategy


def main(args):
    print(vars(args))
    bids_dir = Path(args.bids_dir)
    output_dir = Path(args.output_dir)

    # parse denoise strategy
    denoise_strategy = args.denoise_strategy
    if _valid_strategy(denoise_strategy) and args.globalsignal:
        denoise_strategy += "+gsr"
    strategy = get_denoise_strategy(denoise_strategy)

    # template
    tpl = "MNI152NLin2009cAsym"
    if denoise_strategy == "icaaroma":
        tpl = "MNI152NLin6Asym"

    # atlas
    atlas = args.atlas
    atlas_parameters = mask._load_atlas_setting()[atlas]

    # create root dir
    output_dir = output_dir / "giga_connectome"
    output_dir.mkdir(exist_ok=True)

    working_dir = output_dir / "wd"
    working_dir.mkdir(exist_ok=True)

    # check the list of subjects to run
    fmriprep_bids_layout = BIDSLayout(
        root=bids_dir,
        database_path=None,
        validate=False,
        derivatives=True,
    )
    metadata = get_metadata(fmriprep_bids_layout)

    # create dataset level masks
    (output_dir / "groupmasks" / f"tpl-{tpl}").mkdir(
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
        (output_dir / "groupmasks" / f"tpl-{tpl}" / current_file_name),
    )

    # dataset level atlas correction
    atlas_parameters["resampled_atlase"] = []
    atlas_parameters["masker"] = []
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
        save_path = str(output_dir / "groupmasks" / f"tpl-{tpl}" / filename)
        nib.save(parcellation_resampled, save_path)
        atlas_masker = _get_masker(atlas_parameters, save_path)
        atlas_parameters["resampled_atlases"].append(save_path)
        atlas_parameters["masker"].append(atlas_masker)

    # filter subjects
    select_space = metadata["template"] == tpl
    images = metadata.loc[select_space, "image"]

    # load confounds and maskers
    confounds, sample_mask = load_confounds_strategy(
        images, **denoise_strategy[strategy]
    )

    # denoise
    group_masker = NiftiMasker(
        standardize=True, mask_img=group_mask, smoothing_fwhm=5
    )
    correlation_measure = ConnectivityMeasure(
        kind="correlation", discard_diagonal=True
    )

    data = {}
    for img, cf, sm in zip(images, confounds, sample_mask):
        time_series_voxel = group_masker.fit_transform(
            img, confounds=cf, sample_mask=sm
        )
        denoised_img = group_masker.inverse_transform(time_series_voxel)
        original_key = Path(img).name.split("_desc")[0]

        for desc, atlas_masker in zip(
            atlas_parameters["desc"], atlas_parameters["masker"]
        ):
            # timeseries extraction
            time_series_atlas = atlas_masker.fit_transform(denoised_img)
            correlation_matrix = correlation_measure.fit_transform(
                [time_series_atlas]
            )[0]
            data[original_key] = {
                desc: {
                    "timeseries": time_series_atlas,
                    "connectome": correlation_matrix,
                }
            }


def _get_masker(atlas_parameters, save_path):
    if atlas_parameters["type"] == "dseg":
        atlas_masker = NiftiLabelsMasker(
            labels_img=save_path, standardize=False
        )
    elif atlas_parameters["type"] == "probseg":
        atlas_masker = NiftiMapsMasker(maps_img=save_path, standardize=False)
    return atlas_masker


def _valid_strategy(denoise_strategy):
    return denoise_strategy in ["simple", "scrubbing.2", "scrubbing.5"]
