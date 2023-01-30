from pathlib import Path
import numpy as np
from giga_connectome.bids import get_metadata
from pkg_resources import resource_filename


def test_get_metadata():
    """Check the function can load from different fMRIPrep dataset."""
    # clone a openneuro datalad instance to temporary space
    # run the function
    fmriprep_path = Path(__file__).parent / "data/ds000228-fmriprep"
    df = get_metadata(fmriprep_path, subject="pixar001")
    assert df.shape[0] == 2  # aroma and regular
    assert df.loc[0, "session"] is np.nan
    return
