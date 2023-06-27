"""
Simple code to smoke test the functionality.
"""
from pathlib import Path
from pkg_resources import resource_filename
from giga_connectome.workflow import workflow

import argparse
import pytest
import os

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


@pytest.mark.skipif(
    IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions."
)
def test_smoke(tmp_path):
    bids_dir = resource_filename(
        "giga_connectome", "data/test_data/ds000017-fmriprep22.0.1-downsampled"
    )

    args = argparse.Namespace(
        bids_dir=Path(bids_dir),
        output_dir=tmp_path / "output",
        work_dir=tmp_path / "output/work",
        atlas="Schaefer20187Networks",
        standardize="zscore",
        smoothing_fwhm=5.0,
        denoise_strategy="simple",
        analysis_level="participant",
        participant_label=[],
    )
    if not Path(args.output_dir).exists:
        Path(args.output_dir).mkdir()
    workflow(args)
    # test the group level
    # Smoke test the group level
    args.analysis_level = "group"
    args.standardize = "psc"
    workflow(args)
