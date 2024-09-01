from __future__ import annotations
from typing import Any
import argparse
from pathlib import Path
from typing import Sequence

from giga_connectome import __version__
from giga_connectome.atlas import get_atlas_labels
from giga_connectome.logger import gc_logger

gc_log = gc_logger()

preset_atlas = get_atlas_labels()
deprecations = {
    # parser attribute name:
    # (replacement flag, version slated to be removed in)
    "work-dir": ("--atlases-dir", "0.7.0"),
}


class DeprecatedAction(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str | Sequence[Any] | None,
        option_string: str | None = None,
    ) -> None:
        new_opt, rem_vers = deprecations.get(self.dest, (None, None))
        msg = (
            f"{self.option_strings} has been deprecated and will be removed "
            f"in {rem_vers or 'a later version'}."
        )
        if new_opt:
            msg += f" Please use `{new_opt}` instead."
        gc_log.warning(msg)
        delattr(namespace, self.dest)


def global_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description=(
            "Generate denoised timeseries and Pearson's correlation based "
            "connectomes from fmriprep processed dataset."
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
        help="Level of the analysis that will be performed. Only participant"
        "level is available.",
        choices=["participant"],
    )
    parser.add_argument(
        "-v", "--version", action="version", version=__version__
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
        "-a",
        "--atlases-dir",
        action="store",
        type=Path,
        default=Path("atlases").absolute(),
        help="Path where subject specific segmentations are stored.",
    )
    parser.add_argument(
        "-w",
        "--work-dir",
        action=DeprecatedAction,
        help="This argument is deprecated. Please use --atlas-dir instead.",
    )
    parser.add_argument(
        "--atlas",
        help="The choice of atlas for time series extraction. Default atlas "
        f"choices are: {preset_atlas}. User can pass "
        "a path to a json file containing configuration for their own choice "
        "of atlas. The default is 'Schaefer2018'.",
        default="Schaefer2018",
    )
    parser.add_argument(
        "--denoise-strategy",
        help="The choice of post-processing for denoising. The default "
        "choices are: 'simple', 'simple+gsr', 'scrubbing.2', "
        "'scrubbing.2+gsr', 'scrubbing.5', 'scrubbing.5+gsr', 'acompcor50', "
        "'icaaroma'. User can pass a path to a json file containing "
        "configuration for their own choice of denoising strategy. The default"
        "is 'simple'.",
        default="simple",
    )
    parser.add_argument(
        "--smoothing_fwhm",
        help="Size of the full-width at half maximum in millimeters of "
        "the spatial smoothing to apply to the signal. The default is 5.0.",
        type=float,
        default=5.0,
    )
    parser.add_argument(
        "--reindex-bids",
        help="Reindex BIDS data set, even if layout has already been created.",
        action="store_true",
    )
    parser.add_argument(
        "--bids-filter-file",
        type=Path,
        help="A JSON file describing custom BIDS input filters using PyBIDS."
        "We use the same format as described in fMRIPrep documentation: "
        "https://fmriprep.org/en/latest/faq.html#"
        "how-do-i-select-only-certain-files-to-be-input-to-fmriprep"
        "However, the query filed should always be 'bold'",
    )
    parser.add_argument(
        "--calculate-intranetwork-average-correlation",
        help="Calculate average correlation within each network. This is a "
        "python implementation of the matlab code from the NIAK connectome "
        "pipeline (option A). The default is False.",
        action="store_true",
    )
    parser.add_argument(
        "--verbosity",
        help="""
        Verbosity level.
        """,
        required=False,
        choices=[0, 1, 2, 3],
        default=2,
        type=int,
        nargs=1,
    )
    return parser


def main(argv: None | Sequence[str] = None) -> None:
    """Entry point."""
    parser = global_parser()

    args = parser.parse_args(argv)

    # local import to speed up CLI response
    # when just askig for --help or --version
    from giga_connectome.workflow import workflow

    workflow(args)


if __name__ == "__main__":
    raise RuntimeError(
        "run.py should not be run directly;\n"
        "Please `pip install` and use the `giga_connectome` command"
    )
