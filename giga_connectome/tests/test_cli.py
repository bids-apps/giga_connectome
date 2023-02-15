"""
Simple code to smoke test the functionality.
"""

import argparse
from pathlib import Path
from giga_connectome.workflow import workflow


project_root = Path(__file__).parents[2]
args = argparse.Namespace(
    bids_dir=project_root / "data/ds000114_R2.0.1/derivatives/fmriprep/",
    output_dir=project_root / "output",
    work_dir=project_root / "output/work",
    atlas="Schaefer2018",
    denoise_strategy="simple",
    global_signal=False,
)

if not Path(args.output_dir).exists:
    Path(args.output_dir).mkdir()

workflow(args)
