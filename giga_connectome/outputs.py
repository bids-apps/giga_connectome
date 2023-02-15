import json
from typing import Union, List, Optional
from pathlib import Path

import h5py
from tqdm import tqdm
import numpy as np
from nibabel import Nifti1Image
from nilearn.connectome import ConnectivityMeasure
from nilearn.interfaces.fmriprep import load_confounds_strategy
from nilearn.interfaces.bids import parse_bids_filename
from nilearn.maskers import NiftiMasker, NiftiLabelsMasker, NiftiMapsMasker

from pkg_resources import resource_filename


def get_denoise_strategy_parameters(
    strategy_name: Optional[str] = None,
) -> dict:
    """
    Select denoise strategies and associated parameters.
    The strategy parameters are designed to pass to load_confounds_strategy.

    Parameter
    ---------

    strategy_name : None or str
        Default to None, returns all strategies.
        Name of the denoising strategy options:
        simple, simple+gsr, scrubbing.5, scrubbing.5+gsr,
        scrubbing.2, scrubbing.2+gsr, acompcor50, icaaroma.

    Return
    ------

    dict
        Denosing strategy parameter to pass to load_confounds_strategy.
    """
    strategy_file = resource_filename(
        "giga_connectome", "data/denoise_strategy.json"
    )
    with open(strategy_file, "r") as file:
        benchmark_strategies = json.load(file)

    if isinstance(strategy_name, str) and (
        strategy_name not in benchmark_strategies
    ):
        raise NotImplementedError(
            f"Strategy '{strategy_name}' is not implemented. Select from the"
            f"following: {[*benchmark_strategies]}"
        )

    if strategy_name is None:
        return benchmark_strategies
    return {strategy_name: benchmark_strategies[strategy_name]}


def run_postprocessing_dataset(
    strategy_parameters: dict,
    resampled_atlases: List[Union[str, Path]],
    images: List[Union[str, Path]],
    group_mask: Union[str, Path],
    output_path: Path,
) -> None:
    """
    Generate subject and group level timeseries and connectomes.

    Parameters
    ----------

    strategy_parameters : dict
        Parameters for `load_confounds_strategy`.

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
    atlas = output_path.name.split("_")[0].split("-")[-1]
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
        denoised_img = _denoise_nifti_voxel(
            strategy_parameters, group_masker, img
        )
        # parse file name
        subject, session, specifier = _parse_bids_name(img)
        for desc in atlas_maskers:
            attribute_name = f"{subject}_{specifier}_atlas-{atlas}_desc-{desc}"
            masker = atlas_maskers[desc]
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
                group = _fetch_h5_group(f, subject, session)
                group.create_dataset(
                    f"{attribute_name}_timeseries", data=time_series_atlas
                )
                group.create_dataset(
                    f"{attribute_name}_connectome", data=correlation_matrix
                )

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
    strategy_parameters: dict, group_masker: NiftiMasker, img: str
) -> Nifti1Image:
    """Denoise voxel level data per nifti image."""
    cf, sm = load_confounds_strategy(img, **strategy_parameters)
    time_series_voxel = group_masker.fit_transform(
        img, confounds=cf, sample_mask=sm
    )
    denoised_img = group_masker.inverse_transform(time_series_voxel)
    return denoised_img


def _set_file_flag(output_path: Path) -> str:
    """Find out if new file needs to be created."""
    flag = "w"
    if output_path.exists():
        flag = "a"
    return flag


def _parse_bids_name(img: str) -> List[str]:
    """Get subject, session, and specifier for a fMRIPrep output."""
    reference = parse_bids_filename(img)
    subject = f"sub-{reference['sub']}"
    session = reference.get("ses", None)
    run = reference.get("run", None)
    specifier = f"tast-{reference['task']}"
    if isinstance(session, str):
        session = f"ses-{session}"
        specifier = f"{session}_{specifier}"

    if isinstance(run, str):
        specifier = f"{specifier}_run-{run}"
    return subject, session, specifier


def _fetch_h5_group(f: h5py.File, subject: str, session: str) -> h5py.Group:
    """Determine the level of grouping based on BIDS standard."""
    if subject not in f:
        if session:
            group = f.create_group(f"{subject}/{session}")
        else:
            group = f.create_group(f"{subject}")
    elif session:
        if session not in f[f"{subject}"]:
            group = f[f"{subject}"].create_group(f"{session}")
        else:
            group = f[f"{subject}/{session}"]
    else:
        group = f[f"{subject}"]
    return group


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
