from typing import Union, Optional

import json
from pathlib import Path
import pandas as pd
import numpy as np
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


def get_denoise_strategy(
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


def is_ica_aroma(strategy):
    """Check if the current strategy is ICA AROMA."""
    strategy_preset = strategy["parameters"].get("denoise_strategy", False)
    strategy_user_define = strategy["parameters"].get("strategy", False)
    if strategy_preset or strategy_user_define:
        return (
            strategy_preset == "ica_aroma"
            if strategy_preset
            else "ica_aroma" in strategy_user_define
        )
    else:
        raise ValueError(f"Invalid input dictionary. {strategy['parameters']}")


def denoise_nifti_voxel(
    strategy: dict,
    group_mask: Union[str, Path],
    standardize: Union[str, bool],
    smoothing_fwhm: float,
    img: str,
) -> Nifti1Image:
    """Denoise voxel level data per nifti image."""
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
    reduced_confounds: pd.DataFrame, sample_mask: Optional[np.ndarray]
) -> bool:
    """For scrubbing based strategy, check if regression can be performed."""
    if sample_mask is not None:
        kept_vol = len(sample_mask)
    else:
        kept_vol = reduced_confounds.shape[0]
    # if more noise regressors than volume, this data is not denoisable
    remove = kept_vol < reduced_confounds.shape[1]
    return remove
