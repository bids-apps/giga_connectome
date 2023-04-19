import argparse
from pathlib import Path
from giga_connectome.workflow import workflow


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=(
            "Generate connectome based on denoising strategy for "
            "fmriprep processed dataset."
        ),
    )
    parser.add_argument(
        "bids_dir",
        action="store",
        type=Path,
        help="The directory with the input dataset (e.g. fMRIPrep derivative)"
        "formatted according to the BIDS standard.",
    )
    parser.add_argument(
        "output_dir",
        action="store",
        type=Path,
        help="The directory where the output files should be stored.",
    )
    parser.add_argument(
        "analysis_level",
        help="Level of the analysis that will be performed. Only group level "
        "is allowed as we need to generate a dataset inclusive brain mask.",
        choices=["participant", "group"],
    )
    parser.add_argument(
        "--participant_label",
        help="The label(s) of the participant(s) that should be analyzed. The "
        "label corresponds to sub-<participant_label> from the BIDS spec (so "
        "it does not include 'sub-'). If this parameter is not provided all "
        "subjects should be analyzed. Multiple participants can be specified "
        "with a space separated list.",
        nargs="+",
    )
    parser.add_argument(
        "-w",
        "--work-dir",
        action="store",
        type=Path,
        default=Path("work").absolute(),
        help="Path where intermediate results should be stored.",
    )
    parser.add_argument(
        "--atlas",
        help="The choice of atlas for time series extraction. Default atlas "
        "choices are: 'Schaefer20187Networks, 'MIST', 'DiFuMo'. User can pass "
        "a path to a json file containing configuration for their own choice "
        "of atlas.",
        default="DiFuMo",
    )
    parser.add_argument(
        "--denoise-strategy",
        help="The choice of post-processing for denoising. The default "
        "choices are: 'simple', 'simple+gsr', 'scrubbing.2', "
        "'scrubbing.2+gsr', 'scrubbing.5', 'scrubbing.5+gsr', 'acompcor50', "
        "'icaaroma'. User can pass a path to a json file containing "
        "configuration for their own choice of denoising strategy.",
        default="simple",
    )
    parser.add_argument(
        "--bids-filter-file",
        type=Path,
        help="A JSON file describing custom BIDS input filters using PyBIDS."
        "We use the same format as described in fMRIPrep documentation: "
        "https://fmriprep.org/en/latest/faq.html#"
        "how-do-i-select-only-certain-files-to-be-input-to-fmriprep",
    )
    args = parser.parse_args()

    workflow(args)
