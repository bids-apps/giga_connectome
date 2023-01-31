"""
Process fMRIPrep outputs to timeseries based on denoising strategy.
"""
import argparse
from pathlib import Path

import bids
import nibabel as nib

from nilearn.maskers import NiftiMasker
from nilearn.interfaces.fmriprep import load_confounds_strategy
from giga_connectome.bids import get_metadata
from giga_connectome.denoise import generate_group_mask, get_denoise_strategy


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=(
            "Generate connectome based on denoising strategy for "
            "fmriprep processed dataset."
        ),
    )
    parser.add_argument(
        "output_path",
        action="store",
        type=str,
        help="output path for connectome.",
    )
    parser.add_argument(
        "--fmriprep_path",
        action="store",
        type=str,
        help="Path to a fmriprep detrivative.",
    )
    parser.add_argument(
        "--atlas",
        action="store",
        type=str,
        help="Atlas name (schaefer7networks, MIST, difumo, gordon333)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    print(vars(args))
    # atlas_name = args.atlas
    fmriprep_path = Path(args.fmriprep_path)
    output_path = Path(args.output_path)

    denoise_strategy = get_denoise_strategy()
    fmriprep_bids_layout = bids.BIDSLayout(
        root=fmriprep_path,
        database_path=None,
        validate=False,
        derivatives=True,
    )
    metadata = get_metadata(fmriprep_bids_layout)

    templates = list(metadata["templates"].unique())
    group_masks = {}

    # create dataset level masks for each space
    for tpl in templates:
        current_epis = metadata[metadata["templates"] == tpl]
        current_masks = current_epis["masks"].tolist()
        current_group_mask = generate_group_mask(current_masks, tpl)

        current_file_name = f"space-{tpl}_label-GM_desc-group_mask.nii.gz"
        nib.save(current_group_mask, output_path / current_file_name)

        masker = NiftiMasker(
            standardize=True,
            mask_img=current_group_mask,
            smoothing_fwhm=5,
        )

        # save in disc
        group_masks[tpl] = {
            "file_path": str(output_path / current_file_name),
            "masker": masker,
        }

    # denoise
    images = list(metadata["images"])
    templates = list(metadata["templates"])

    for img, tpl in zip(images, templates):
        for strategy in denoise_strategy:
            confounds, sample_mask = load_confounds_strategy(
                img, **denoise_strategy[strategy]
            )
            current_masker = group_masks[tpl][masker]
            time_series_voxel = current_masker.fit_transform(
                img, confounds=confounds, sample_mask=sample_mask
            )
            # make sure the time series are in 32-bits
            time_series_voxel = time_series_voxel.astype("float32")
            denoised_img = current_masker.inverse_transform(time_series_voxel)
            original_key = Path(img).name.split("_desc")[0]
            current_file_name = f"{original_key}_desc-{strategy}_bold.nii.gz"
            nib.save(denoised_img, output_path / current_file_name)

    # timeseries extraction


if __name__ == "__main__":
    main()
