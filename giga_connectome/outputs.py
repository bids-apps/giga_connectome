import json
from typing import Union, List
from pathlib import Path

import h5py
from tqdm import tqdm
import numpy as np
from nibabel import Nifti1Image
from nilearn.connectome import ConnectivityMeasure
from nilearn.interfaces import fmriprep
from nilearn.maskers import NiftiMasker, NiftiLabelsMasker, NiftiMapsMasker

from giga_connectome.utils import parse_bids_name
from pkg_resources import resource_filename


PRESET_STRATEGIES = [
    "simple",
    "simple+gsr",
    "scrubbing.2",
    "scrubbing.2+gsr",
    "scrubbing.5",
    "scrubbing.5+gsr",
    "acompcor50",
    "icaaroma",
]


def get_denoise_strategy_parameters(
    strategy: str,
) -> dict:
    """
    Select denoise strategies and associated parameters.
    The strategy parameters are designed to pass to load_confounds_strategy.

    Parameter
    ---------

    strategy : str
        Name of the denoising strategy options:
        simple, simple+gsr, scrubbing.5, scrubbing.5+gsr,
        scrubbing.2, scrubbing.2+gsr, acompcor50, icaaroma.
        Or the path to a configuration json file.

    Return
    ------

    dict
        Denosing strategy parameter to pass to load_confounds_strategy.
    """
    if strategy in PRESET_STRATEGIES:
        config_path = resource_filename(
            "giga_connectome", f"data/denoise_strategy/{strategy}.json"
        )
    elif Path(strategy).exists():
        config_path = Path(strategy)
    else:
        raise ValueError(f"Invalid input: {strategy}")

    with open(config_path, "r") as file:
        benchmark_strategy = json.load(file)

    lc_function = getattr(fmriprep, benchmark_strategy["function"])
    benchmark_strategy.update({"function": lc_function})
    return benchmark_strategy


def run_postprocessing_dataset(
    strategy: dict,
    resampled_atlases: List[Union[str, Path]],
    images: List[Union[str, Path]],
    group_mask: Union[str, Path],
    output_path: Path,
    analysis_level: str,
) -> None:
    """
    Generate subject and group level timeseries and connectomes.

    Parameters
    ----------

    strategy : dict
        Parameters for `load_confounds_strategy` or `load_confounds`.

    resampled_atlases : list of str or pathlib.Path
        Atlas niftis resampled to the common space of the dataset.

    images : list of str or pathlib.Path
        Preprocessed Nifti images for post processing

    group_mask : str or pathlib.Path
        Group level grey matter mask.

    output_path:
        Full path to output file, named in the following format:
            output_dir / atlas-<atlas>_desc-<strategy_name>.h5
    """
    atlas = output_path.name.split("atlas-")[-1].split("_")[0]
    print("set up masker objects")
    group_masker = NiftiMasker(
        standardize=True, mask_img=group_mask, smoothing_fwhm=5
    )

    atlas_maskers, connectomes = {}, {}
    for atlas_path in resampled_atlases:
        if isinstance(atlas_path, str):
            atlas_path = Path(atlas_path)
        desc = atlas_path.name.split("desc-")[-1].split("_")[0]
        atlas_maskers[desc] = _get_masker(atlas_path)
        connectomes[desc] = []

    correlation_measure = ConnectivityMeasure(
        kind="correlation", discard_diagonal=True
    )

    # transform data
    print("processing subjects")
    for img in tqdm(images):
        # process timeseries
        denoised_img = _denoise_nifti_voxel(strategy, group_masker, img)
        # parse file name
        subject, session, specifier = parse_bids_name(img)
        for desc, masker in atlas_maskers.items():
            attribute_name = f"{subject}_{specifier}_atlas-{atlas}_desc-{desc}"
            if denoised_img:
                (
                    time_series_atlas,
                    correlation_matrix,
                ) = _generate_subject_timeseries_connectome(
                    masker, correlation_measure, denoised_img
                )
                connectomes[desc].append(correlation_matrix)
                # dump to h5
                flag = _set_file_flag(output_path)
                with h5py.File(output_path, flag) as f:
                    group = _fetch_h5_group(
                        f, subject, session, analysis_level
                    )
                    group.create_dataset(
                        f"{attribute_name}_timeseries", data=time_series_atlas
                    )
                    group.create_dataset(
                        f"{attribute_name}_connectome", data=correlation_matrix
                    )
            else:
                time_series_atlas, correlation_matrix = None, None
                print(f"{attribute_name}: no volume after scrubbing")

    if analysis_level == "group":
        print("create group connectome")
        for desc in connectomes:
            average_connectome = np.mean(
                np.array(connectomes[desc]), axis=0
            ).astype(np.float32)
            with h5py.File(output_path, "a") as f:
                f.create_dataset(
                    f"atlas-{atlas}_desc-{desc}_connectome",
                    data=average_connectome,
                )


def _generate_subject_timeseries_connectome(
    masker: Union[NiftiMapsMasker, NiftiLabelsMasker],
    correlation_measure: ConnectivityMeasure,
    denoised_img: Nifti1Image,
) -> List[np.array]:
    """Generate connectome and timeseries per nifti image."""
    time_series_atlas = masker.fit_transform(denoised_img)
    correlation_matrix = correlation_measure.fit_transform(
        [time_series_atlas]
    )[0]
    # float 32 instead of 64
    time_series_atlas = time_series_atlas.astype(np.float32)
    correlation_matrix = correlation_matrix.astype(np.float32)
    return time_series_atlas, correlation_matrix


def _denoise_nifti_voxel(
    strategy: dict, group_masker: NiftiMasker, img: str
) -> Nifti1Image:
    """Denoise voxel level data per nifti image."""

    cf, sm = strategy["function"](img, **strategy["parameters"])
    if _check_exclusion(cf, sm):
        return None
    time_series_voxel = group_masker.fit_transform(
        img, confounds=cf, sample_mask=sm
    )
    denoised_img = group_masker.inverse_transform(time_series_voxel)
    return denoised_img


def _check_exclusion(reduced_confounds, sample_mask):
    """For scrubbing based strategy, check if regression can be performed."""
    if sample_mask is not None:
        kept_vol = len(sample_mask)
    else:
        kept_vol = reduced_confounds.shape[0]
    # more noise regressors than volume
    remove = kept_vol < reduced_confounds.shape[1]
    return remove


def _set_file_flag(output_path: Path) -> str:
    """Find out if new file needs to be created."""
    flag = "w"
    if output_path.exists():
        flag = "a"
    return flag


def _fetch_h5_group(
    f: h5py.File, subject: str, session: str, analysis_level: str
) -> Union[h5py.File, h5py.Group]:
    """Determine the level of grouping based on BIDS standard."""
    if analysis_level == "group":
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
    # subject level
    if not session:
        return f
    elif session not in f:
        return f.create_group(f"{session}")
    else:
        return f[f"{session}"]


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
