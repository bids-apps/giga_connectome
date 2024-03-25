"""
Set up templateflow with customised altases.
Download atlases that are relevant.
"""

from pathlib import Path

from giga_connectome.logger import gc_logger

gc_log = gc_logger()


def fetch_tpl_atlas():
    """Download datasets from templateflow."""
    import templateflow.api as tf

    atlases = ["Schaefer2018", "DiFuMo"]
    for atlas in atlases:
        tf_path = tf.get("MNI152NLin2009cAsym", atlas=atlas)
        if isinstance(tf_path, list) and len(tf_path) > 0:
            gc_log.info(f"{atlas} exists.")
    # download MNI grey matter template
    tf.get("MNI152NLin2009cAsym", label="GM")


def download_mist():
    """Download mist atlas and convert to templateflow format."""
    import templateflow

    tf_path = templateflow.api.get("MNI152NLin2009bAsym", atlas="BASC")
    if isinstance(tf_path, list) and len(tf_path) > 0:
        gc_log.info("BASC / MIST atlas exists.")
        return

    # download and convert
    import importlib.util
    import sys
    import shutil

    spec = importlib.util.spec_from_file_location(
        "mist2templateflow",
        Path(__file__).parent / "mist2templateflow/mist2templateflow.py",
    )
    mist2templateflow = importlib.util.module_from_spec(spec)
    sys.modules["module.name"] = mist2templateflow
    spec.loader.exec_module(mist2templateflow)
    mist2templateflow.convert_basc(
        templateflow.conf.TF_HOME, Path(__file__).parent / "tmp"
    )
    shutil.rmtree(Path(__file__).parent / "tmp")


def main():
    fetch_tpl_atlas()
    download_mist()


if __name__ == "__main__":
    main()
