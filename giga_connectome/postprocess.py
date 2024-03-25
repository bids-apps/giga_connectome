from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

import h5py
import numpy as np
from bids.layout import BIDSImageFile
from nilearn.connectome import ConnectivityMeasure
from nilearn.maskers import NiftiLabelsMasker, NiftiMapsMasker

from giga_connectome import utils
from giga_connectome.connectome import generate_timeseries_connectomes
from giga_connectome.denoise import STRATEGY_TYPE, denoise_nifti_voxel
from giga_connectome.logger import gc_logger
from giga_connectome.utils import progress_bar

gc_log = gc_logger()


def run_postprocessing_dataset(
    strategy: STRATEGY_TYPE,
    resampled_atlases: Sequence[str | Path],
    images: Sequence[BIDSImageFile],
    group_mask: str | Path,
    standardize: str | bool,
    smoothing_fwhm: float,
    output_path: Path,
    analysis_level: str,
    calculate_average_correlation: bool = False,
) -> None:
    """
    Generate subject and group level timeseries and connectomes.

    The time series data is denoised as follow:

    - Time series extractions through label or map maskers are performed \
        on the denoised nifti file. Denoising steps are performed on the \
        voxel level:

        - spatial smoothing

        - detrend, only if high pass filter is not applied through confounds

        - Regress out confounds

        - standardize

    - Extract time series from atlas

    - Compute correlation matrix

    - Optional: average correlation within each parcel.

    - Save timeseries and correlation matrix to h5 file

    - Optional: Create average correlation matrix across subjects when using \
        group level analysis.

    Parameters
    ----------

    strategy : dict
        Parameters for `load_confounds_strategy` or `load_confounds`.

    resampled_atlases : list of str or pathlib.Path
        Atlas niftis resampled to the common space of the dataset.

    images : list of BIDSImageFile
        Preprocessed Nifti images for post processing

    group_mask : str or pathlib.Path
        Group level grey matter mask.

    standardize : str or bool
        Standardization options used in nilearn, passed to nilearn masker.
        Options: True, False, "psc"

    smoothing_fwhm : float
        Smoothing kernel size, passed to nilearn masker.

    output_path:
        Full path to output file, named in the following format:
        output_dir / atlas-<atlas>_desc-<strategy_name>.h5

    analysis_level : str
        Level of analysis, either "participant" or "group".

    calculate_average_correlation : bool
        Whether to calculate average correlation within each parcel.
    """
    atlas = output_path.name.split("atlas-")[-1].split("_")[0]
    atlas_maskers: dict[str, (NiftiLabelsMasker | NiftiMapsMasker)] = {}
    connectomes: dict[str, list[np.ndarray[Any, Any]]] = {}
    for atlas_path in resampled_atlases:
        if isinstance(atlas_path, str):
            atlas_path = Path(atlas_path)
        desc = atlas_path.name.split("desc-")[-1].split("_")[0]
        atlas_maskers[desc] = _get_masker(atlas_path)
        connectomes[desc] = []

    correlation_measure = ConnectivityMeasure(
        kind="correlation", vectorize=False, discard_diagonal=False
    )

    # transform data
    with progress_bar(text="Processing subject") as progress:
        task = progress.add_task(
            description="processing subject", total=len(images)
        )

        for img in images:
            print()
            gc_log.info(f"Processing image:\n{img.filename}")

            # process timeseries
            denoised_img = denoise_nifti_voxel(
                strategy, group_mask, standardize, smoothing_fwhm, img.path
            )
            # parse file name
            subject, session, specifier = utils.parse_bids_name(img.path)
            for desc, masker in atlas_maskers.items():
                attribute_name = (
                    f"{subject}_{specifier}_atlas-{atlas}_desc-{desc}"
                )
                if not denoised_img:
                    time_series_atlas, correlation_matrix = None, None

                    gc_log.info(f"{attribute_name}: no volume after scrubbing")

                    progress.update(task, advance=1)
                    continue

                # extract timeseries and connectomes
                (
                    correlation_matrix,
                    time_series_atlas,
                ) = generate_timeseries_connectomes(
                    masker,
                    denoised_img,
                    group_mask,
                    correlation_measure,
                    calculate_average_correlation,
                )
                connectomes[desc].append(correlation_matrix)

                # dump to h5
                flag = _set_file_flag(output_path)
                with h5py.File(output_path, flag) as f:
                    group = _fetch_h5_group(f, subject, session)
                    timeseries_dset = group.create_dataset(
                        f"{attribute_name}_timeseries", data=time_series_atlas
                    )
                    timeseries_dset.attrs["RepetitionTime"] = img.entities[
                        "RepetitionTime"
                    ]
                    group.create_dataset(
                        f"{attribute_name}_connectome", data=correlation_matrix
                    )

                progress.update(task, advance=1)

        gc_log.info(f"Saved to:\n{output_path}")

    if analysis_level == "group":
        gc_log.info("Create group connectome")

        for desc in connectomes:
            average_connectome = np.mean(
                np.array(connectomes[desc]), axis=0
            ).astype(np.float32)
            with h5py.File(output_path, "a") as f:
                f.create_dataset(
                    f"atlas-{atlas}_desc-{desc}_connectome",
                    data=average_connectome,
                )


def _set_file_flag(output_path: Path) -> str:
    """Find out if new file needs to be created."""
    flag = "a" if output_path.exists() else "w"
    return flag


def _fetch_h5_group(
    file: h5py.File, subject: str, session: str | None
) -> h5py.File | h5py.Group:
    """Determine the level of grouping based on BIDS standard."""
    if subject not in file:
        return (
            file.create_group(f"{subject}/{session}")
            if session
            else file.create_group(subject)
        )
    elif session:
        return (
            file[subject].create_group(session)
            if session not in file[subject]
            else file[f"{subject}/{session}"]
        )
    else:
        return file[subject]


def _get_masker(atlas_path: Path) -> NiftiLabelsMasker | NiftiMapsMasker:
    """Get the masker object based on the templateflow file name suffix."""
    atlas_type = atlas_path.name.split("_")[-1].split(".nii")[0]
    if atlas_type == "dseg":
        atlas_masker = NiftiLabelsMasker(
            labels_img=atlas_path, standardize=False
        )
    elif atlas_type == "probseg":
        atlas_masker = NiftiMapsMasker(maps_img=atlas_path, standardize=False)
    return atlas_masker
