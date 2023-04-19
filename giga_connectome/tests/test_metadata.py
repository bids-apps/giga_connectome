import pytest

from pathlib import Path
import bids
from giga_connectome.metadata import get_metadata


def test_get_metadata():
    """Check the function can load from different fMRIPrep dataset."""
    # clone a openneuro datalad instance to temporary space
    # run the function
    fmriprep_path = Path(__file__).parent / "data/ds000228-fmriprep"
    fmriprep_bids_layout = bids.BIDSLayout(
        root=fmriprep_path,
        database_path=None,
        validate=False,
        derivatives=True,
    )
    df = get_metadata(fmriprep_bids_layout, subject=["pixar001", "pixar002"])
    assert df.shape[0] == 4  # aroma and regular for two subjects
    assert "session" not in df.columns.tolist()

    # check another dataset with session info
    fmriprep_path = Path(__file__).parent / "data/ds003007-fmriprep"
    fmriprep_bids_layout = bids.BIDSLayout(
        root=fmriprep_path,
        database_path=None,
        validate=False,
        derivatives=True,
    )
    df = get_metadata(fmriprep_bids_layout, subject=["01", "02"])
    assert df.shape[0] == 8  # aroma and regular
    assert set(df.loc[:, "session"].unique()) == {"post", "pre"}

    with pytest.warns(UserWarning, match="The following BIDS entities"):
        get_metadata(fmriprep_bids_layout, space="MNI152NLin2009cAsym")
