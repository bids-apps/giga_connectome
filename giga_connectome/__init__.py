import contextlib

__packagename__ = "giga_connectome"
__copyright__ = "2025, BIDS-Apps"

with contextlib.suppress(ImportError):
    from ._version import __version__


__all__ = [
    "__copyright__",
    "__packagename__",
    "__version__",
]
