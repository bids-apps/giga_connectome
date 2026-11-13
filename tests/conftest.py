from pathlib import Path

import pytest


@pytest.fixture
def data_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def bids_dir() -> Path:
    """Downsampled fMRIPrep derivatives of ds000017 (``tox -e test_data``)."""
    return (
        Path(__file__).parent
        / "data"
        / "test_data"
        / "ds000017-fmriprep22.0.1-downsampled-nosurface"
    )
