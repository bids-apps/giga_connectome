import os
import json
from typing import Union, List

from pathlib import Path
from tqdm import tqdm
import nibabel as nib
from nilearn.image import resample_to_img
from nibabel import Nifti1Image
from pkg_resources import resource_filename


PRESET_ATLAS = ["DiFuMo", "MIST", "Schaefer20187Networks"]


def load_atlas_setting(atlas: Union[str, Path, dict]):
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
        - parameters : BIDS entities that fits templateflow conventions
            except desc.
        - desc : templateflow entities description. Can be a list if user
            wants to include multiple resolutions of the atlas.
        - templateflow_dir : Path to templateflow director.
            If null, use the system default.

    Returns
    -------
    dict
        Path to the atlas files.
    """
    atlas_config = _check_altas_config(atlas)
    print(atlas_config)

    # load template flow
    templateflow_dir = atlas_config.get("templateflow_dir")
    if isinstance(templateflow_dir, str):
        templateflow_dir = Path(templateflow_dir)
        if templateflow_dir.exists():
            os.environ["TEMPLATEFLOW_HOME"] = str(templateflow_dir.resolve())
        else:
            raise FileNotFoundError

    import templateflow

    if isinstance(atlas_config["desc"], str):
        desc = [atlas_config["desc"]]
    else:
        desc = atlas_config["desc"]

    parcellation = {}
    for d in desc:
        p = templateflow.api.get(
            **atlas_config["parameters"],
            raise_empty=True,
            desc=d,
            extension="nii.gz",
        )
        parcellation[d] = p
    return {
        "name": atlas_config["name"],
        "file_paths": parcellation,
        "type": atlas_config["parameters"]["suffix"],
    }


def resample_atlas_collection(
    template: str,
    atlas_config: dict,
    group_mask_dir: Path,
    group_mask: Nifti1Image,
) -> List[Path]:
    """Resample a atlas collection to group grey matter mask.

    Parameters
    ----------
    template: str
        Templateflow template name. This template should match the template of
        `all_masks`.

    atlas_config: dict
        Atlas name. Currently support Schaefer20187Networks, MIST, DiFuMo.

    group_mask_dir: pathlib.Path
        Path to where the outputs are saved.

    group_mask : nibabel.nifti1.Nifti1Image
        EPI (grey matter) mask for the current group of subjects.

    Returns
    -------
    List of pathlib.Path
        Paths to atlases sampled to group level grey matter mask.
    """
    print("Resample atlas to group grey matter mask.")
    resampled_atlases = []
    for desc in tqdm(atlas_config["file_paths"]):
        parcellation = atlas_config["file_paths"][desc]
        parcellation_resampled = resample_to_img(
            parcellation, group_mask, interpolation="nearest"
        )
        filename = (
            f"tpl-{template}_"
            f"atlas-{atlas_config['name']}_"
            "res-dataset_"
            f"desc-{desc}_"
            f"{atlas_config['type']}.nii.gz"
        )
        save_path = group_mask_dir / filename
        nib.save(parcellation_resampled, save_path)
        resampled_atlases.append(save_path)
    return resampled_atlases


def _check_altas_config(atlas: Union[str, Path, dict]) -> dict:
    """Load the configuration file.

    Parameters
    ----------
    atlas : Union[str, Path, dict]
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
    # load the file first if the input is not already a dictionary
    if isinstance(atlas, (str, Path)):
        if atlas in PRESET_ATLAS:
            config_path = resource_filename(
                "giga_connectome", f"data/atlas/{atlas}.json"
            )
        elif Path(atlas).exists():
            config_path = Path(atlas)

        with open(config_path, "r") as file:
            atlas = json.load(file)

    keys = list(atlas.keys())
    minimal_keys = ["name", "parameters", "desc", "templateflow_dir"]
    common_keys = set(minimal_keys).intersection(set(keys))
    if isinstance(atlas, dict) and common_keys != set(minimal_keys):
        raise KeyError(
            "Invalid dictionary input. Input should"
            " contain minimally the following keys: 'name', "
            "'parameters', 'desc', 'templateflow_dir'. Found "
            f"{keys}"
        )
    return atlas
