import numpy as np
import pytest
from nibabel import Nifti1Image
from nilearn import datasets

from giga_connectome import mask


def test_generate_group_mask():
    """Generate group epi grey matter mask and resample atlas."""
    data = datasets.fetch_development_fmri(n_subjects=3)
    imgs = data.func

    group_epi_mask = mask.generate_group_mask(imgs)
    # match the post processing details: https://osf.io/wjtyq
    assert group_epi_mask.shape == (50, 59, 50)
    diff_tpl = mask.generate_group_mask(imgs, template="MNI152NLin2009aAsym")
    assert diff_tpl.shape == (50, 59, 50)

    # test bad inputs
    with pytest.raises(
        ValueError, match="TemplateFlow does not supply template blah"
    ):
        mask.generate_group_mask(imgs, template="blah")


def test_check_mask_affine():
    """Check odd affine detection."""

    img_base = np.zeros([5, 5, 6])
    processed_vol = img_base.copy()
    processed_vol[2:4, 2:4, 2:4] += 1
    processed = Nifti1Image(processed_vol, np.eye(4))
    weird = Nifti1Image(processed_vol, np.eye(4) * np.array([1, 1, 1.5, 1]).T)
    weird2 = Nifti1Image(processed_vol, np.eye(4) * np.array([1, 1, 1.6, 1]).T)
    exclude = mask._check_mask_affine(
        [processed, processed, processed, processed, weird, weird, weird2]
    )
    assert len(exclude) == 3
    assert exclude == [4, 5, 6]


def test_get_consistent_masks():
    """Check odd affine detection."""
    mask_imgs = [
        f"sub-{i + 1:2d}_task-rest_space-MNI_desc-brain_mask.nii.gz"
        for i in range(10)
    ]
    exclude = [1, 2, 5]
    (
        cleaned_func_masks,
        weird_mask_identifiers,
    ) = mask._get_consistent_masks(mask_imgs, exclude)
    assert len(cleaned_func_masks) == 7
    assert len(weird_mask_identifiers) == 3
