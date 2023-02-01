"""
Process fMRIPrep outputs to timeseries based on denoising strategy.
"""
import argparse
from pathlib import Path

from bids import BIDSLayout
import nibabel as nib

from giga_connectome.metadata import get_metadata
from giga_connectome import mask


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
    return parser.parse_args()


def main():
    args = parse_args()
    print(vars(args))
    fmriprep_path = Path(args.fmriprep_path)
    output_path = Path(args.output_path)

    atlas_settings = mask._load_atlas_setting()

    fmriprep_bids_layout = BIDSLayout(
        root=fmriprep_path,
        database_path=None,
        validate=False,
        derivatives=True,
    )
    # check the list of subjects to run
    metadata = get_metadata(fmriprep_bids_layout)
    metadata.to_csv(output_path / "func_scans_list.tsv", sep="\t")

    templates = list(metadata["template"].unique())

    # create dataset level masks for each space
    for tpl in templates:
        current_epis = metadata[metadata["template"] == tpl]
        current_masks = current_epis["mask"].tolist()
        current_group_mask = mask.generate_group_mask(current_masks, tpl)

        current_file_name = f"space-{tpl}_label-GM_desc-group_mask.nii.gz"
        nib.save(current_group_mask, output_path / current_file_name)

    # dataset level atlas correction
    for _, parameters in atlas_settings.items():
        for desc in parameters["desc"]:
            for tpl in templates:
                current_group_mask = str(
                    output_path
                    / f"space-{tpl}_label-GM_desc-group_mask.nii.gz"
                )
                (
                    parcellation_resampled,
                    filename,
                ) = mask.resample_atlas2groupmask(
                    parameters["atlas"], current_group_mask, desc
                )
                nib.save(parcellation_resampled, output_path / filename)


if __name__ == "__main__":
    main()
