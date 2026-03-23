import contextlib

with contextlib.suppress(ImportError):
    from ._version import __version__


__all__ = [
    "__version__",
]
