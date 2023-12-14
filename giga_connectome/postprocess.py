from typing import Union, List
from pathlib import Path

import h5py
from tqdm import tqdm
import numpy as np
from nilearn.connectome import ConnectivityMeasure
from nilearn.maskers import NiftiLabelsMasker, NiftiMapsMasker
from bids.layout import BIDSImageFile

from giga_connectome import utils
from giga_connectome.connectome import generate_timeseries_connectomes
from giga_connectome.denoise import denoise_nifti_voxel
from giga_connectome.logger import gc_logger

gc_log = gc_logger()


def run_postprocessing_dataset(
    strategy: dict,
    atlas: str,
    resampled_atlases: List[Union[str, Path]],
    images: List[BIDSImageFile],
    group_mask: Union[str, Path],
    standardize: Union[str, bool],
    smoothing_fwhm: float,
    output_path: Path,
    analysis_level: str,
    calculate_average_correlation: bool = False,
    output_to_bids: bool = False,
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

    atlas : dict
        Atlas settings.

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
        Full path to output directory.

    analysis_level : str
        Level of analysis, either "participant" or "group".

    calculate_average_correlation : bool
        Whether to calculate average correlation within each parcel.
    """
    atlas_maskers, connectomes = {}, {}
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
    gc_log.info("Processing subject")

    # single output file per subject when output is not BIDS compliant
    if not output_to_bids:
        subject, _, _ = utils.parse_bids_name(images[0].path)
        filename = utils.output_filename(
            Path(images[0].filename).stem,
            atlas["name"],
            strategy["name"],
            output_to_bids,
        )
        connectome_path = output_path / subject / "func" / filename
        connectome_path = utils.check_path(connectome_path)

    for img in tqdm(images):
        print()
        gc_log.info(f"Processing image:\n{img.filename}")

        # process timeseries
        denoised_img = denoise_nifti_voxel(
            strategy, group_mask, standardize, smoothing_fwhm, img.path
        )
        # parse file name
        subject, session, specifier = utils.parse_bids_name(img.path)

        # one output file per input file when output is BIDS compliant
        if output_to_bids:
            connectome_path = output_path / subject
            if session:
                connectome_path = connectome_path / session
            filename = utils.output_filename(
                Path(img.filename).stem,
                atlas["name"],
                strategy["name"],
                output_to_bids,
            )
            connectome_path = connectome_path / "func" / filename
            connectome_path = utils.check_path(connectome_path)

        for desc, masker in atlas_maskers.items():
            attribute_name = (
                f"{subject}_{specifier}_atlas-{atlas['name']}_desc-{desc}"
            )
            if not denoised_img:
                time_series_atlas, correlation_matrix = None, None

                gc_log.info(f"{attribute_name}: no volume after scrubbing")

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
            flag = _set_file_flag(connectome_path)
            with h5py.File(connectome_path, flag) as f:
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

        gc_log.info(f"Saved to:\n{connectome_path}")

    if analysis_level == "group":
        connectome_path = (
            output_path
            / "group"
            / utils.output_filename(
                "",
                atlas["name"],
                strategy["name"],
                output_to_bids,
            )
        )
        connectome_path = utils.check_path(connectome_path)

        gc_log.info("Create group connectome")
        gc_log.info(connectome_path)

        for desc in connectomes:
            average_connectome = np.mean(
                np.array(connectomes[desc]), axis=0
            ).astype(np.float32)
            with h5py.File(connectome_path, "a") as f:
                f.create_dataset(
                    f"atlas-{atlas['name']}_desc-{desc}_connectome",
                    data=average_connectome,
                )

        gc_log.info(f"Saved to:\n{connectome_path}")


def _set_file_flag(output_path: Path) -> str:
    """Find out if new file needs to be created."""
    flag = "w"
    if output_path.exists():
        flag = "a"
    return flag


def _fetch_h5_group(
    f: h5py.File, subject: str, session: str
) -> Union[h5py.File, h5py.Group]:
    """Determine the level of grouping based on BIDS standard."""
    if subject not in f:
        return (
            f.create_group(f"{subject}/{session}")
            if session
            else f.create_group(f"{subject}")
        )
    elif session:
        return (
            f[f"{subject}"].create_group(f"{session}")
            if session not in f[f"{subject}"]
            else f[f"{subject}/{session}"]
        )
    else:
        return f[f"{subject}"]


def _get_masker(atlas_path: Path) -> Union[NiftiLabelsMasker, NiftiMapsMasker]:
    """Get the masker object based on the templateflow file name suffix."""
    atlas_type = atlas_path.name.split("_")[-1].split(".nii")[0]
    if atlas_type == "dseg":
        atlas_masker = NiftiLabelsMasker(
            labels_img=atlas_path, standardize=False
        )
    elif atlas_type == "probseg":
        atlas_masker = NiftiMapsMasker(maps_img=atlas_path, standardize=False)
    return atlas_masker
