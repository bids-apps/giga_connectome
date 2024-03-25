__packagename__ = "giga_connectome"
__copyright__ = "2021, SIMEXP"

try:
    from ._version import __version__
except ImportError:
    pass

from .atlas import load_atlas_setting
from .denoise import get_denoise_strategy
from .mask import generate_gm_mask_atlas
from .postprocess import run_postprocessing_dataset

__all__ = [
    "__copyright__",
    "__packagename__",
    "__version__",
    "generate_gm_mask_atlas",
    "load_atlas_setting",
    "run_postprocessing_dataset",
    "get_denoise_strategy",
]
