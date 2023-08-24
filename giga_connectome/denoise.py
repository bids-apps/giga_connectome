import json
from pathlib import Path

from nilearn.interfaces import fmriprep

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


def is_ica_aroma(strategy: str) -> bool:
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
        return (
            strategy_preset == "ica_aroma"
            if strategy_preset
            else "ica_aroma" in strategy_user_define
        )
    else:
        raise ValueError(f"Invalid input dictionary. {strategy['parameters']}")
