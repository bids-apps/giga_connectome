from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, TypedDict

import nibabel as nib
from nibabel import Nifti1Image
from nilearn.image import resample_to_img
from pkg_resources import resource_filename

from giga_connectome.logger import gc_logger
from giga_connectome.utils import progress_bar

gc_log = gc_logger()

ATLAS_CONFIG_TYPE = TypedDict(
    "ATLAS_CONFIG_TYPE",
    {
        "name": str,
        "parameters": Dict[str, str],
        "desc": List[str],
        "templateflow_dir": Any,
    },
)

ATLAS_SETTING_TYPE = TypedDict(
    "ATLAS_SETTING_TYPE",
    {"name": str, "file_paths": Dict[str, List[Path]], "type": str},
)

deprecations = {
    # parser attribute name:
    # (replacement, version slated to be removed in)
    "Schaefer20187Networks": ("Schaefer2018", "0.7.0"),
}


def load_atlas_setting(
    atlas: str | Path | dict[str, Any],
) -> ATLAS_SETTING_TYPE:
    """Load atlas details for templateflow api to fetch.
    The setting file can be configured for atlases not included in the
    templateflow collections, but user has to organise their files to
    templateflow conventions to use the tool.

    Parameters
    ----------
    atlas: str or pathlib.Path or dict
        Path to atlas configuration json file or a python dictionary.
        It should contain the following fields:

        - name : name of the atlas.

        - parameters : BIDS entities that fits templateflow conventions \
            except desc.

        - desc : templateflow entities description. Can be a list if user \
            wants to include multiple resolutions of the atlas.

        - templateflow_dir : Path to templateflow director. \
            If null, use the system default.

    Returns
    -------
    dict
        Path to the atlas files.
    """
    atlas_config = _check_altas_config(atlas)
    gc_log.info(atlas_config)

    # load template flow
    templateflow_dir = atlas_config.get("templateflow_dir")
    if isinstance(templateflow_dir, str):
        templateflow_dir = Path(templateflow_dir)
        if templateflow_dir.exists():
            os.environ["TEMPLATEFLOW_HOME"] = str(templateflow_dir.resolve())
        else:
            raise FileNotFoundError

    import templateflow

    parcellation = {}
    for d in atlas_config["desc"]:
        p = templateflow.api.get(
            **atlas_config["parameters"],
            raise_empty=True,
            desc=d,
            extension="nii.gz",
        )
        if isinstance(p, Path):
            p = [p]
        parcellation[d] = p
    return {
        "name": atlas_config["name"],
        "file_paths": parcellation,
        "type": atlas_config["parameters"]["suffix"],
    }


def resample_atlas_collection(
    subject_seg_file_names: list[str],
    atlas_config: ATLAS_SETTING_TYPE,
    subject_mask_dir: Path,
    subject_mask: Nifti1Image,
) -> list[Path]:
    """Resample a atlas collection to group grey matter mask.

    Parameters
    ----------
    subject_atlas_file_names: list of str
        File names of subject atlas segmentations.

    atlas_config: dict
        Atlas name. Currently support Schaefer20187Networks, MIST, DiFuMo.

    subject_mask_dir: pathlib.Path
        Path to where the outputs are saved.

    subject_mask : nibabel.nifti1.Nifti1Image
        EPI (grey matter) mask for the subject.

    Returns
    -------
    list of pathlib.Path
        Paths to subject specific segmentations created from atlases sampled
        to individual grey matter mask.
    """
    gc_log.info("Resample atlas to group grey matter mask.")
    subject_seg = []

    with progress_bar(text="Resampling atlases") as progress:
        task = progress.add_task(
            description="resampling", total=len(atlas_config["file_paths"])
        )

        for seg_file, desc in zip(
            subject_seg_file_names, atlas_config["file_paths"]
        ):
            parcellation = atlas_config["file_paths"][desc]
            parcellation_resampled = resample_to_img(
                parcellation, subject_mask, interpolation="nearest"
            )
            save_path = subject_mask_dir / seg_file
            nib.save(parcellation_resampled, save_path)
            subject_seg.append(save_path)

        progress.update(task, advance=1)

    return subject_seg


def get_atlas_labels() -> List[str]:
    """Get the list of available atlas labels."""
    atlas_dir = resource_filename("giga_connectome", "data/atlas")
    return [p.stem for p in Path(atlas_dir).glob("*.json")]


def _check_altas_config(
    atlas: str | Path | dict[str, Any],
) -> ATLAS_CONFIG_TYPE:
    """Load the configuration file.

    Parameters
    ----------
    atlas : str | Path | dict
        Atlas name or configuration file path.

    Returns
    -------
    dict
        valid atlas configuration.

    Raises
    ------
    KeyError
        atlas configuration not containing the correct keys.
    """
    if isinstance(atlas, str) and atlas in deprecations:
        new_name, version = deprecations[atlas]
        gc_log.warning(
            f"{atlas} has been deprecated and will be removed in "
            f"{version}. Please use {new_name} instead."
        )
        atlas = new_name

    # load the file first if the input is not already a dictionary
    atlas_dir = resource_filename("giga_connectome", "data/atlas")
    preset_atlas = [p.stem for p in Path(atlas_dir).glob("*.json")]

    if isinstance(atlas, (str, Path)):
        if atlas in preset_atlas:
            config_path = Path(
                resource_filename(
                    "giga_connectome", f"data/atlas/{atlas}.json"
                )
            )
        elif Path(atlas).exists():
            config_path = Path(atlas)
        else:
            raise FileNotFoundError(
                f"Atlas configuration file {atlas} not found."
            )

        with open(config_path, "r") as file:
            atlas_config = json.load(file)
    else:
        atlas_config = atlas

    minimal_keys = ["name", "parameters", "desc", "templateflow_dir"]
    keys = list(atlas_config.keys())
    common_keys = set(minimal_keys).intersection(set(keys))
    if common_keys != set(minimal_keys):
        raise KeyError(
            "Invalid dictionary input. Input should"
            " contain minimally the following keys: 'name', "
            "'parameters', 'desc', 'templateflow_dir'. Found "
            f"{keys}"
        )

    # cast to list of string
    if isinstance(atlas_config["desc"], (str, int)):
        desc = [atlas_config["desc"]]
    else:
        desc = atlas_config["desc"]
    atlas_config["desc"] = [str(x) for x in desc]

    return atlas_config
