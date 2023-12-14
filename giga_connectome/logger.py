"""General logger for the cohort_creator package."""
from __future__ import annotations

import logging


def gc_logger(log_level: str = "INFO") -> logging.Logger:
    FORMAT = "%(message)s"

    logging.basicConfig(
        level=log_level,
        format=FORMAT,
        datefmt="[%X]",
    )

    return logging.getLogger("giga_connectome")
