"""General logger for the cohort_creator package."""

from __future__ import annotations

import logging

from rich.logging import RichHandler


def gc_logger(log_level: str = "INFO") -> logging.Logger:
    # FORMAT = '\n%(asctime)s - %(name)s - %(levelname)s\n\t%(message)s\n'
    FORMAT = "%(message)s"

    logging.basicConfig(
        level=log_level,
        format=FORMAT,
        datefmt="[%X]",
        handlers=[RichHandler()],
    )

    return logging.getLogger("giga_connectome")
