"""
Simple code to smoke test the functionality.
"""

import argparse
from pathlib import Path
from giga_connectome.workflow import workflow


project_root = Path(__file__).parents[2]
args = argparse.Namespace(
    bids_dir=Path("/home/haoting/Downloads/fmriprep-20.2.1lts"),
    output_dir=project_root / "output",
    work_dir=project_root / "output/work",
    atlas="Schaefer20187Networks",
    denoise_strategy="simple",
    participant_label=["pixar001", "pixar002"],
    analysis_level="participant",
)

if not Path(args.output_dir).exists:
    Path(args.output_dir).mkdir()

workflow(args)

# test the group level
args = argparse.Namespace(
    bids_dir=Path("/home/haoting/Downloads/fmriprep-20.2.1lts"),
    output_dir=project_root / "output",
    work_dir=project_root / "output/work",
    atlas="Schaefer20187Networks",
    denoise_strategy="simple",
    participant_label=["pixar001", "pixar002"],
    analysis_level="group",
)

workflow(args)
