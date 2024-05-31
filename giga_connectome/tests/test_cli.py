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
def test_smoke(tmp_path, caplog):
    bids_dir = resource_filename(
        "giga_connectome",
        "data/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface",
    )
    output_dir = tmp_path / "output"
    atlases_dir = tmp_path / "atlases"
    work_dir = tmp_path / "work"

    if not Path(output_dir).exists:
        Path(output_dir).mkdir()

    main(
        [
            "--participant_label",
            "1",
            "-w",
            str(work_dir),
            "-a",
            str(atlases_dir),
            "--atlas",
            "Schaefer2018",
            "--denoise-strategy",
            "simple",
            "--reindex-bids",
            "--calculate-intranetwork-average-correlation",
            "--bids-filter-file",
            str(Path(bids_dir).parent / "bids_filter.json"),
            str(bids_dir),
            str(output_dir),
            "participant",
        ]
    )
    # check outputs
    assert "has been deprecated" in caplog.text.splitlines()[0]

    output_folder = output_dir / "sub-1" / "ses-timepoint1" / "func"

    base = (
        "sub-1_ses-timepoint1_task-probabilisticclassification"
        "_run-01_seg-Schaefer2018100Parcels7Networks"
    )
    ts_base = (
        "sub-1_ses-timepoint1_task-probabilisticclassification"
        "_run-01_desc-denoiseSimple"
    )
    relmat_file = output_folder / (
        base + "_meas-PearsonCorrelation" + "_desc-denoiseSimple_relmat.tsv"
    )
    assert relmat_file.exists()
    relmat = pd.read_csv(relmat_file, sep="\t")
    assert len(relmat) == 100
    json_file = relmat_file = output_folder / (ts_base + "_timeseries.json")
    assert json_file.exists()
    with open(json_file, "r") as f:
        content = json.load(f)
        assert content.get("SamplingFrequency") == 0.5

    timeseries_file = relmat_file = output_folder / (
        base + "_desc-denoiseSimple_timeseries.tsv"
    )
    assert timeseries_file.exists()
    timeseries = pd.read_csv(timeseries_file, sep="\t")
    assert len(timeseries.columns) == 100

    # immediately rerun should cover the case where the output already exists
    main(
        [
            "--participant_label",
            "1",
            "-a",
            str(atlases_dir),
            "--atlas",
            "Schaefer2018",
            "--denoise-strategy",
            "simple",
            "--calculate-intranetwork-average-correlation",
            "--bids-filter-file",
            str(Path(bids_dir).parent / "bids_filter.json"),
            str(bids_dir),
            str(output_dir),
            "participant",
        ]
    )

    # deleate gm mask to trigger rerun the atlas generation

    gm_path = (
        atlases_dir
        / "sub-1"
        / "func"
        / "sub-1_space-MNI152NLin2009cAsym_res-2_label-GM_mask.nii.gz"
    )
    # delete gm_path
    gm_path.unlink()
    # rerun
    main(
        [
            "--participant_label",
            "1",
            "-a",
            str(atlases_dir),
            "--atlas",
            "Schaefer2018",
            "--denoise-strategy",
            "simple",
            "--calculate-intranetwork-average-correlation",
            "--bids-filter-file",
            str(Path(bids_dir).parent / "bids_filter.json"),
            str(bids_dir),
            str(output_dir),
            "participant",
        ]
    )
