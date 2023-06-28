import pytest

import bids
from giga_connectome import metadata
from pkg_resources import resource_filename


def test_get_metadata():
    """Check the function can load from different fMRIPrep dataset."""
    # check another dataset with session info
    fmriprep_path = resource_filename(
        "giga_connectome",
        "data/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface",
    )
    fmriprep_bids_layout = bids.BIDSLayout(
        root=fmriprep_path,
        validate=False,
        derivatives=True,
    )
    df = metadata.get_metadata(fmriprep_bids_layout, subject=["1", "2"])
    # aroma and regular, two session, two tasks (2 runs and 3 runs)
    assert df.shape[0] == 40
    print(df)
    assert set(df.loc[:, "session"].unique()) == {"timepoint1", "timepoint2"}

    with pytest.warns(UserWarning, match="The following BIDS entities"):
        metadata.get_metadata(
            fmriprep_bids_layout, space="MNI152NLin2009cAsym"
        )


def test_load_bids_entities():
    with pytest.raises(ValueError) as exc_info:
        metadata._load_bids_entities("blah")
    assert str(exc_info.value) == "File type blah is not defined."
