import argparse

from main import main


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter,
    description=(
        "Generate connectome based on denoising strategy for "
        "fmriprep processed dataset."
    ),
)
parser.add_argument(
    "bids_dir",
    help="The directory with the input dataset "
    "formatted according to the BIDS standard.",
)
parser.add_argument(
    "output_dir",
    help="The directory where the output files "
    "should be stored. If you are running group level analysis "
    "this folder should be prepopulated with the results of the"
    "participant level analysis.",
)
parser.add_argument(
    "analysis_level",
    help="Level of the analysis that will be performed. "
    "Multiple participant level analyses can be run independently "
    "(in parallel) using the same output_dir.",
    choices=["participant", "group"],
)
parser.add_argument(
    "--atlas",
    help="The choice of atlas for time series extraction.",
    choices=["Schaefer2018", "MIST", "DiFuMo"],
)
parser.add_argument(
    "--denoise_strategy",
    help="The choice of post-processing for denoising.",
    choices=["simple", "scrubbing.2", "scrubbing.5", "acompcor50", "icaaroma"],
)
parser.add_argument(
    "--globalsignal",
    help="Apply global signal regressor. Only available to simple and "
    "scrubbing strategies.",
    action="store_true",
)

args = parser.parse_args()

main(args)
