import json

# import pandas as pd

# from nilearn.signal import clean
# from nilearn.interfaces.fmriprep import load_confounds_strategy

# from giga_connectome.atlas import (
#     create_atlas_masker,
#     get_atlas_dimensions,
# )
from pkg_resources import resource_filename


def get_denoise_strategy(strategy_name=None):
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
        print("Process all strategies.")
        return benchmark_strategies
    (f"Process strategy '{strategy_name}'.")
    return {strategy_name: benchmark_strategies[strategy_name]}
