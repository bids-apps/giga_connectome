import pytest
import numpy as np
from giga_connectome.mask import generate_group_mask, resample_atlas2groupmask
from nilearn import datasets


def test_mask():
    """Generate group epi grey matter mask and resample atlas."""
    data = datasets.fetch_development_fmri(n_subjects=3)
    imgs = data.func

    group_epi_mask = generate_group_mask(imgs)
    # match the post processing details: https://osf.io/wjtyq
    assert group_epi_mask.shape == (50, 59, 50)

    parcellation_resampled, filename = resample_atlas2groupmask(
        "DiFuMo", "64dimensions", group_epi_mask
    )
    assert parcellation_resampled.shape[:3] == (50, 59, 50)
    np.testing.assert_array_equal(
        parcellation_resampled.affine, group_epi_mask.affine
    )
