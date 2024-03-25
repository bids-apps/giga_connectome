"""
Simple code to smoke test the functionality.
"""

from pathlib import Path

import json
import pytest
from pkg_resources import resource_filename

import pandas as pd

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
            "--reindex-bids",
            "--calculate-intranetwork-average-correlation",
            str(bids_dir),
            str(output_dir),
            "participant",
        ]
    )

    output_folder = output_dir / "sub-1" / "ses-timepoint1" / "func"

    base = (
        "sub-1_ses-timepoint1_task-probabilisticclassification"
        "_run-01_space-MNI152NLin2009cAsym_res-2"
        "_atlas-Schaefer20187Networks"
    )

    relmat_file = output_folder / (
        base
        + "_meas-PearsonCorrelation"
        + "_desc-100Parcels7NetworksSimple_relmat.tsv"
    )
    assert relmat_file.exists()
    relmat = pd.read_csv(relmat_file, sep="\t")
    assert len(relmat) == 100

    json_file = relmat_file = output_folder / (base + "_timeseries.json")
    assert json_file.exists()
    with open(json_file, "r") as f:
        content = json.load(f)
        assert content.get("SamplingFrequency") == 0.5

    timeseries_file = relmat_file = output_folder / (
        base + "_desc-100Parcels7NetworksSimple_timeseries.tsv"
    )
    assert timeseries_file.exists()
    timeseries = pd.read_csv(timeseries_file, sep="\t")
    assert len(timeseries.columns) == 100
