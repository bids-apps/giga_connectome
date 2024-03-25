from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, List, TypedDict, Union

import numpy as np
import pandas as pd
from nibabel import Nifti1Image
from nilearn.interfaces import fmriprep
from nilearn.maskers import NiftiMasker
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

# More refined type not possible with python <= 3.9?
# STRATEGY_TYPE = TypedDict(
#     "STRATEGY_TYPE",
#     {
#         "name": str,
#         "function": Callable[
#             ..., tuple[pd.DataFrame, Union[np.ndarray[Any, Any], None]]
#         ],
#         "parameters": dict[str, str | list[str]],
#     },
# )
STRATEGY_TYPE = TypedDict(
    "STRATEGY_TYPE",
    {
        "name": str,
        "function": Callable[..., Any],
        "parameters": Dict[str, Union[str, List[str]]],
    },
)


def get_denoise_strategy(
    strategy: str,
) -> STRATEGY_TYPE:
    """
    Select denoise strategies and associated parameters.
    The strategy parameters are designed to pass to load_confounds_strategy.

    Parameter
    ---------

    strategy : str
        Name of the denoising strategy options: \
        simple, simple+gsr, scrubbing.5, scrubbing.5+gsr, \
        scrubbing.2, scrubbing.2+gsr, acompcor50, icaaroma.
        Or the path to a configuration json file.

    Return
    ------

    dict
        Denosing strategy parameter to pass to load_confounds_strategy.
    """
    if strategy in PRESET_STRATEGIES:
        config_path: str | Path = resource_filename(
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


def is_ica_aroma(strategy: STRATEGY_TYPE) -> bool:
    """Check if the current strategy is ICA AROMA.

    Parameters
    ----------
    strategy : dict
        Denoising strategy dictionary. See :func:`get_denoise_strategy`.

    Returns
    -------
    bool
        True if the strategy is ICA AROMA.
    """
    strategy_preset = strategy["parameters"].get("denoise_strategy", False)
    strategy_user_define = strategy["parameters"].get("strategy", False)
    if strategy_preset or strategy_user_define:
        return strategy_preset == "ica_aroma"
    elif isinstance(strategy_user_define, list):
        return "ica_aroma" in strategy_user_define
    else:
        raise ValueError(f"Invalid input dictionary. {strategy['parameters']}")


def denoise_nifti_voxel(
    strategy: STRATEGY_TYPE,
    group_mask: str | Path,
    standardize: bool,
    smoothing_fwhm: float,
    img: str,
) -> Nifti1Image:
    """Denoise voxel level data per nifti image.

    Parameters
    ----------
    strategy : dict
        Denoising strategy parameter to pass to load_confounds_strategy.
    group_mask : str | Path
        Path to the group mask.
    standardize : bool
        Standardize the data. If True, zscore the data. If False, do \
            not standardize.
    smoothing_fwhm : float
        Smoothing kernel size in mm.
    img : str
        Path to the nifti image to denoise.

    Returns
    -------
    Nifti1Image
        Denoised nifti image.
    """
    cf, sm = strategy["function"](img, **strategy["parameters"])
    if _check_exclusion(cf, sm):
        return None

    # if high pass filter is not applied through cosines regressors,
    # then detrend
    detrend = "cosine00" not in cf.columns
    group_masker = NiftiMasker(
        mask_img=group_mask,
        detrend=detrend,
        standardize=standardize,
        smoothing_fwhm=smoothing_fwhm,
    )

    time_series_voxel = group_masker.fit_transform(
        img, confounds=cf, sample_mask=sm
    )
    denoised_img = group_masker.inverse_transform(time_series_voxel)
    return denoised_img


def _check_exclusion(
    reduced_confounds: pd.DataFrame,
    sample_mask: np.ndarray[Any, Any] | None,
) -> bool:
    """For scrubbing based strategy, check if regression can be performed."""
    if sample_mask is not None:
        kept_vol = len(sample_mask)
    else:
        kept_vol = reduced_confounds.shape[0]
    # if more noise regressors than volume, this data is not denoisable
    remove = kept_vol < reduced_confounds.shape[1]
    return remove
