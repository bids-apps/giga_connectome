import numpy as np
from nibabel import Nifti1Image
from nilearn.connectome import ConnectivityMeasure
from nilearn.maskers import NiftiLabelsMasker, NiftiMasker

from giga_connectome.connectome import generate_timeseries_connectomes


def _extract_time_series_voxel(img, mask, confounds=None, smoothing_fwhm=None):
    masker = NiftiMasker(
        standardize=True, mask_img=mask, smoothing_fwhm=smoothing_fwhm
    )
    time_series_voxel = masker.fit_transform(img, confounds=confounds)
    return time_series_voxel, masker


def _simulate_img():
    """Simulate data with one 'spot'"""
    data = np.zeros([8, 8, 8, 100])
    time_series = np.random.randn(1, 1, 3, data.shape[3])
    # parcel 1 with intra correlation
    data[4, 4, 3, :] = time_series[0, 0, 0, :]
    data[4, 4, 4, :] = time_series[0, 0, 0, :] + time_series[0, 0, 1, :]
    # parcel 2 with intra correlation (and some correlation with parcel 1)
    data[4, 4, 5, :] = time_series[0, 0, 1, :]
    data[4, 4, 6, :] = time_series[0, 0, 1, :] + time_series[0, 0, 2, :]
    corr = np.corrcoef(data[4, 4, 3:7, :])
    img = Nifti1Image(data, np.eye(4))

    mask_v = np.zeros(data.shape[0:3])
    mask_v[4, 4, 3:7] = 1
    mask = Nifti1Image(mask_v, np.eye(4))

    atlas = np.zeros(data.shape[0:3])
    atlas[4, 4, 3:5] = 1
    atlas[4, 4, 5:7] = 2
    atlas = Nifti1Image(atlas, np.eye(4))
    return img, mask, atlas, (corr[1, 0], corr[2, 3])


def test_calculate_intranetwork_correlation():
    img, mask, atlas, corr = _simulate_img()
    # brute force version of intranetwork_correlation
    time_series_voxel, masker_voxel = _extract_time_series_voxel(img, mask)
    assert (
        abs(np.corrcoef(time_series_voxel.transpose())[1, 0] - corr[0]) < 1e-10
    )
    assert (
        abs(np.corrcoef(time_series_voxel.transpose())[2, 3] - corr[1]) < 1e-10
    )

    denoised_img = masker_voxel.inverse_transform(time_series_voxel)

    correlation_measure = ConnectivityMeasure(
        kind="correlation", vectorize=False, discard_diagonal=False
    )
    conn, _, _ = generate_timeseries_connectomes(
        masker=NiftiLabelsMasker(labels_img=atlas),
        denoised_img=denoised_img,
        group_mask=mask,
        correlation_measure=correlation_measure,
        calculate_average_correlation=True,
    )  # output of the function is in float32
    assert np.abs(corr[0] - conn[0, 0]) < 1e-6
    assert np.abs(corr[1] - conn[1, 1]) < 1e-6
