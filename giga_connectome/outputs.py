import json
from typing import Union, List, Optional

from pathlib import Path

import h5py
import numpy as np
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


def generate_subject_level_data(
    strategy_parameters: dict,
    resampled_atlases: List[str],
    images: List[str],
    group_mask: Union[str, Path],
    output_path: Path,
) -> None:
    """
    Generate subject level timeseries and connectomes.

    """
    # load confounds and maskers
    confounds, sample_mask = load_confounds_strategy(
        images, **strategy_parameters
    )

    # set up masker objects
    group_masker = NiftiMasker(
        standardize=True, mask_img=group_mask, smoothing_fwhm=5
    )

    atlas_maskers = {}
    for atlas_path in resampled_atlases:
        desc = atlas_path.split("desc-")[-1].split("_")[0]
        atlas_maskers[desc] = _get_masker(atlas_path)

    correlation_measure = ConnectivityMeasure(
        kind="correlation", discard_diagonal=True
    )

    # transform data
    connectomes = {desc: [] for desc in atlas_maskers}
    for img, cf, sm in zip(images, confounds, sample_mask):
        time_series_voxel = group_masker.fit_transform(
            img, confounds=cf, sample_mask=sm
        )
        denoised_img = group_masker.inverse_transform(time_series_voxel)
        # parse file name
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
        atlas = output_path.name.split("_")[0].split("-")[-1]

        for desc in atlas_maskers:
            attribute_name = f"{subject}_{specifier}_atlas-{atlas}_desc-{desc}"
            masker = atlas_maskers[desc]
            time_series_atlas = masker.fit_transform(denoised_img)
            correlation_matrix = correlation_measure.fit_transform(
                [time_series_atlas]
            )[0]
            # float 32 instead of 64
            time_series_atlas = time_series_atlas.astype(np.float32)
            correlation_matrix = correlation_matrix.astype(np.float32)
            connectomes[desc].append(correlation_matrix)

            # dump to h5
            flag = "w"
            if output_path.exists():
                flag = "a"

            with h5py.File(output_path, flag) as f:
                group = _fetch_h5_group(f, subject, session)
                group.create_dataset(
                    f"{attribute_name}_timeseries", data=time_series_atlas
                )
                group.create_dataset(
                    f"{attribute_name}_connectome", data=correlation_matrix
                )

        for desc in connectomes:
            average_connectome = np.mean(connectomes[desc]).astype(np.float32)
            with h5py.File(output_path, "a") as f:
                f.create_dataset(
                    "atlas-{atlas}_desc-{desc}_connectome",
                    data=average_connectome,
                )


def _fetch_h5_group(f, subject, session):
    """Determine which level the file is in."""
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


def _get_masker(atlas_path: str) -> Union[NiftiLabelsMasker, NiftiMapsMasker]:
    """Get the masker object based on the templateflow file name suffix."""
    atlas_type = atlas_path.split("_")[-1].split(".nii")[0]
    if atlas_type == "dseg":
        atlas_masker = NiftiLabelsMasker(
            labels_img=atlas_path, standardize=False
        )
    elif atlas_type == "probseg":
        atlas_masker = NiftiMapsMasker(maps_img=atlas_path, standardize=False)
    return atlas_masker
