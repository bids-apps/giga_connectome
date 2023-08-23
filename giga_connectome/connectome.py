from pathlib import Path
from typing import Union
import numpy as np
from nilearn.maskers import NiftiMasker
from nilearn.image import load_img
from nibabel import Nifti1Image


def build_size_roi(mask, labels_roi):
    """Extract labels and size of ROIs given a atlas.
    The atlas parcels must be discrete segmentations.

    Adapted from:
    https://github.com/SIMEXP/niak/blob/master/commands/SI_processing/niak_build_size_roi.m
    [SIZE_ROI,LABELS_ROI] = BUILD_SIZE_ROI(MASK)

    Parameters
    ----------
    mask : np.ndarray
        Mask of the ROI. Voxels belonging to no region are coded with 0,
        those belonging to region `I` are coded with `I` (`I` being a
        positive integer).

    labels_roi : np.ndarray
        Labels of of region I.

    Returns
    -------
    np.ndarray
        Size of the ROI.
    """

    nb_roi = len(labels_roi)
    size_roi = np.zeros([nb_roi, 1])

    for num_r in range(nb_roi):
        size_roi[num_r] = np.count_nonzero(mask == labels_roi[num_r])

    return size_roi


def calculate_intranetwork_correlation(
    correlation_matrix: np.array,
    masker_labels: np.array,
    time_series_atlas: np.array,
    group_mask: Union[str, Path, Nifti1Image],
    atlas_image: Union[str, Path, Nifti1Image],
) -> np.array:
    """Calculate the average functional correlation within each parcel.
    Currently we only support discrete segmentations.

    Parameters
    ----------
    correlation_matrix : np.array
        N by N Pearson's correlation matrix.

    masker_labels : np.array
        Labels of each parcels in the atlas.

    time_series_atlas : np.array
        Time series extracted from each parcels.

    group_mask : Union[str, Path]
        Group grey matter mask.

    atlas_image : Union[str, Path, Nifti1Image]
        3D atlas image.

    Returns
    -------
    np.array
        Pearson's correlation matrix with the diagnonal replaced with
        average correlation within each parcel.
    """
    if isinstance(atlas_image, (str, Path)):
        atlas_image = load_img(atlas_image)

    if len(atlas_image.shape) > 3:
        raise NotImplementedError("Only support 3D discrete segmentations.")
    # flatten the atlas label image to a vector
    atlas_voxel_flatten = NiftiMasker(
        standardize=False, mask_img=group_mask
    ).fit_transform(atlas_image)
    size_parcels = build_size_roi(atlas_voxel_flatten, masker_labels)
    # calculate the standard deviation of time series in each parcel
    var_parcels = time_series_atlas.var(axis=0)
    var_parcels = np.reshape(var_parcels, (var_parcels.shape[0], 1))
    # detact invalid parcels
    mask_empty = (size_parcels == 0) | (size_parcels == 1)

    # calculate average functional correlation within each parcel
    avg_intranetwork_correlation = (
        (size_parcels * size_parcels) * var_parcels - size_parcels
    ) / (size_parcels * (size_parcels - 1))
    avg_intranetwork_correlation[mask_empty] = 0
    avg_intranetwork_correlation = avg_intranetwork_correlation.reshape(-1)
    # replace the diagnonal with average functional correlation
    idx_diag = np.diag_indices(correlation_matrix.shape[0])
    correlation_matrix[idx_diag] = avg_intranetwork_correlation
    return correlation_matrix, avg_intranetwork_correlation


def generate_timeseries_connectomes(
    masker,
    denoised_img,
    group_mask,
    correlation_measure,
    calculate_average_correlation,
):
    time_series_atlas = masker.fit_transform(denoised_img)
    correlation_matrix = correlation_measure.fit_transform(
        [time_series_atlas]
    )[0]
    masker_labels = masker.labels_
    # average correlation within each parcel
    if calculate_average_correlation:
        (
            correlation_matrix,
            avg_intranetwork_correlation,
        ) = calculate_intranetwork_correlation(
            correlation_matrix,
            masker_labels,
            time_series_atlas,
            group_mask,
            masker.labels_img_,
        )
    # float 32 instead of 64
    time_series_atlas = time_series_atlas.astype(np.float32)
    correlation_matrix = correlation_matrix.astype(np.float32)
    return correlation_matrix, time_series_atlas
