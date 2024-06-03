from giga_connectome.denoise import denoise_meta_data, get_denoise_strategy
from pkg_resources import resource_filename
from numpy import testing


def test_denoise_nifti_voxel():
    img_file = resource_filename(
        "giga_connectome",
        "data/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface/sub-1/ses-timepoint1/func/sub-1_ses-timepoint1_task-probabilisticclassification_run-01_space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz",
    )
    strategy = get_denoise_strategy("scrubbing.2")
    meta_data = denoise_meta_data(
        strategy=strategy,
        img=img_file,
    )
    assert len(meta_data["ConfoundRegressors"]) == 36
    assert meta_data["NumberOfVolumesDiscardedByMotionScrubbing"] == 12
    assert meta_data["NumberOfVolumesDiscardedByNonsteadyStatesDetector"] == 2
    testing.assert_almost_equal(
        meta_data["MeanFramewiseDisplacement"], 0.107, decimal=3
    )

    strategy = get_denoise_strategy("simple")
    meta_data = denoise_meta_data(
        strategy=strategy,
        img=img_file,
    )
    assert len(meta_data["ConfoundRegressors"]) == 30
    assert meta_data["NumberOfVolumesDiscardedByMotionScrubbing"] == 0
    assert meta_data["NumberOfVolumesDiscardedByNonsteadyStatesDetector"] == 2
    testing.assert_almost_equal(
        meta_data["MeanFramewiseDisplacement"], 0.107, decimal=3
    )
