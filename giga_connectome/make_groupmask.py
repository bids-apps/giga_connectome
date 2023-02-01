"""
Process fMRIPrep outputs to timeseries based on denoising strategy.
"""
# TODO: the output structutre is not fully bids
import argparse
from pathlib import Path

import pandas as pd
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

    # create root dir
    output_path = output_path / "groupmasks"
    output_path.mkdir(exist_ok=True)

    atlas_settings = mask._load_atlas_setting()
    # check the list of subjects to run
    if not (output_path / "func_scans_list.tsv").exists():
        fmriprep_bids_layout = BIDSLayout(
            root=fmriprep_path,
            database_path=None,
            validate=False,
            derivatives=True,
        )
        metadata = get_metadata(fmriprep_bids_layout)
        metadata.to_csv(output_path / "func_scans_list.tsv", sep="\t")
    else:
        metadata = pd.read_csv(
            output_path / "func_scans_list.tsv", sep="\t", index_col=0
        )

    templates = list(metadata["template"].unique())

    # create dataset level masks for each space
    for tpl in templates:
        (output_path / f"tpl-{tpl}").mkdir(exist_ok=True)
        current_epis = metadata[metadata["template"] == tpl]
        current_masks = current_epis["mask"].tolist()
        # no grey matter mask is supplied with MNI152NLin6Asym
        # so we are fixed at using the most common space from fmriprep output
        current_group_mask = mask.generate_group_mask(
            current_masks, "MNI152NLin2009cAsym"
        )

        current_file_name = (
            f"tpl-{tpl}_" "res-dataset_label-GM_desc-group_mask.nii.gz"
        )
        nib.save(
            current_group_mask,
            (output_path / f"tpl-{tpl}" / current_file_name),
        )

        # dataset level atlas correction
        for key, parameters in atlas_settings.items():
            for desc in parameters["desc"]:
                parcellation_resampled = mask.resample_atlas2groupmask(
                    key,
                    desc,
                    current_group_mask,
                )
                filename = (
                    f"tpl-{tpl}_"
                    f"atlas-{parameters['atlas']}_"
                    "res-dataset_"
                    f"desc-{desc}_"
                    f"{parameters['type']}.nii.gz"
                )
                nib.save(
                    parcellation_resampled,
                    (output_path / f"tpl-{tpl}" / filename),
                )


if __name__ == "__main__":
    main()
