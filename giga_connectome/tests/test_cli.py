"""
Simple code to smoke test the functionality.
"""

from pathlib import Path

import h5py
import pytest
from pkg_resources import resource_filename

from giga_connectome import __version__
from giga_connectome.run import main


def test_version(capsys):
    try:
        main(["-v"])
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert __version__ == captured.out.split()[0]


def test_help(capsys):
    try:
        main(["-h"])
    except SystemExit:
        pass
    captured = capsys.readouterr()
    assert "Generate denoised timeseries" in captured.out


@pytest.mark.smoke
def test_smoke(tmp_path, capsys):
    bids_dir = resource_filename(
        "giga_connectome",
        "data/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface",
    )
    bids_filter_file = resource_filename(
        "giga_connectome", "data/test_data/bids_filter.json"
    )
    output_dir = tmp_path / "output"
    work_dir = tmp_path / "output/work"

    if not Path(output_dir).exists:
        Path(output_dir).mkdir()

    main(
        [
            "--participant_label",
            "1",
            "-w",
            str(work_dir),
            "--atlas",
            "Schaefer20187Networks",
            "--denoise-strategy",
            "simple",
            "--standardize",
            "zscore",
            "--reindex-bids",
            "--calculate-intranetwork-average-correlation",
            str(bids_dir),
            str(output_dir),
            "participant",
        ]
    )
    # check output
    output_group = (
        output_dir
        / "sub-1"
        / "ses-timepoint1"
        / "func"
        / (
            "sub-1_ses-timepoint1_task-probabilisticclassification_run-01_"
            "space-MNI152NLin2009cAsym_res-2_"
            "atlas-Schaefer20187Networks_meas-PearsonCorrelation_"
            "desc-simple_relmat.h5"
        )
    )
    basename = (
        "sub-1_ses-timepoint1_task-probabilisticclassification_run-01_"
        "atlas-Schaefer20187Networks_desc-100Parcels7Networks_timeseries"
    )
    with h5py.File(output_group, "r") as f:
        data = f[f"sub-1/ses-timepoint1/{basename}"]
        assert data.attrs.get("RepetitionTime") == 2.0

    main(
        [
            "-w",
            str(work_dir),
            "--atlas",
            "Schaefer20187Networks",
            "--denoise-strategy",
            "simple",
            "--standardize",
            "psc",
            "--bids-filter-file",
            str(bids_filter_file),
            str(bids_dir),
            str(output_dir),
            "group",
        ]
    )

    # check output
    output_group = (
        output_dir
        / "group"
        / "atlas-Schaefer20187Networks_meas-PearsonCorrelation_desc-simple_relmat.h5"
    )
    basename = (
        "atlas-Schaefer20187Networks_desc-100Parcels7Networks_connectome"
    )
    with h5py.File(output_group, "r") as f:
        data = f[f"{basename}"]
        assert data.shape == (100, 100)
