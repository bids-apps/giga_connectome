import pytest
import numpy as np
from giga_connectome.mask import generate_group_mask
from nilearn import datasets


def test_generate_group_mask():
    """Generate group epi grey matter mask and resample atlas."""
    data = datasets.fetch_development_fmri(n_subjects=3)
    imgs = data.func

    group_epi_mask = generate_group_mask(imgs)
    # match the post processing details: https://osf.io/wjtyq
    assert group_epi_mask.shape == (50, 59, 50)
    diff_tpl = generate_group_mask(imgs, template="MNI152NLin2009aAsym")
    assert diff_tpl.shape == (50, 59, 50)

    # test bad inputs
    with pytest.raises(
        ValueError, match="TemplateFlow does not supply template blah"
    ):
        generate_group_mask(imgs, template="blah")
