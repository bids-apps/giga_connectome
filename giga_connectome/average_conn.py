import numpy as np


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
