"""
Set up templateflow with customised altases.
Download atlases that are relevant.
"""

import importlib.util
import shutil
import sys

from pathlib import Path

import templateflow as tf

from giga_connectome.logger import gc_logger

gc_log = gc_logger()


def fetch_tpl_atlas() -> None:
    """Download datasets from templateflow."""
    atlases = ["Schaefer2018", "DiFuMo", "HOSPA", "HOCPA", "HOCPAL"]
    for atlas in atlases:
        tf_path = tf.api.get("MNI152NLin2009cAsym", atlas=atlas)
        if isinstance(tf_path, list) and len(tf_path) > 0:
            gc_log.info(f"{atlas} exists.")
        else:
            gc_log.error(f"{atlas} does not exist.")
    # download MNI grey matter template
    tf.api.get("MNI152NLin2009cAsym", label="GM")


def download_mist() -> None:
    """Download mist atlas and convert to templateflow format."""
    tf_path = tf.api.get("MNI152NLin2009bAsym", atlas="BASC")
    if isinstance(tf_path, list) and len(tf_path) > 0:
        gc_log.info("BASC / MIST atlas exists.")
        return

    # download and convert
    spec = importlib.util.spec_from_file_location(
        "mist2templateflow",
        Path(__file__).parent / "mist2templateflow/mist2templateflow.py",
    )
    mist2templateflow = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = mist2templateflow
    spec.loader.exec_module(mist2templateflow)
    mist2templateflow.convert_basc(
        tf.conf.TF_HOME, Path(__file__).parent / "tmp"
    )
    shutil.rmtree(Path(__file__).parent / "tmp")


def main() -> None:
    fetch_tpl_atlas()
    download_mist()


if __name__ == "__main__":
    main()
