"""
Simple code to smoke test the functionality.
"""
from pathlib import Path
from pkg_resources import resource_filename
from giga_connectome.workflow import workflow

import argparse
import pytest
import os

import h5py

IN_GITHUB_ACTIONS = os.getenv("GITHUB_ACTIONS") == "true"


@pytest.mark.skipif(
    IN_GITHUB_ACTIONS, reason="Test doesn't work in Github Actions."
)
def test_smoke(tmp_path):
    bids_dir = resource_filename(
        "giga_connectome",
        "data/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface",
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
        participant_label=["1"],
    )
    if not Path(args.output_dir).exists:
        Path(args.output_dir).mkdir()
    workflow(args)

    # Smoke test the group level
    args.analysis_level = "group"
    args.standardize = "psc"
    args.participant_label = []
    workflow(args)

    output_group = (
        Path(args.output_dir) / "atlas-Schaefer20187Networks_desc-simple.h5"
    )
    basename = (
        "sub-1_ses-timepoint1_task-probabilisticclassification_run-01_"
        "atlas-Schaefer20187Networks_desc-100Parcels7Networks_timeseries"
    )
    with h5py.File(output_group, "r") as f:
        data = f[f"sub-1/ses-timepoint1/{basename}"]
        assert data.attrs.get("RepetitionTime") == 2.0
