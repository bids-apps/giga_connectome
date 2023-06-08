import os
import re
import json
from typing import Optional, Union, List, Tuple

from pathlib import Path
from tqdm import tqdm
import nibabel as nib
from nilearn.masking import compute_multi_epi_mask
from nilearn.image import (
    resample_to_img,
    new_img_like,
    get_data,
    math_img,
    load_img,
)
from nibabel import Nifti1Image
import numpy as np
from scipy.ndimage import binary_closing

from pkg_resources import resource_filename


PRESET_ATLAS = ["DiFuMo", "MIST", "Schaefer20187Networks"]


def resample_atlas_collection(
    template: str,
    atlas_config: dict,
    group_mask_dir: Path,
    group_mask: Nifti1Image,
) -> List[Path]:
    """
    Resample a atlas collection to group grey matter mask.

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


def generate_group_mask(
    imgs: list,
    template: str = "MNI152NLin2009cAsym",
    templateflow_dir: Optional[Path] = None,
    n_iter: int = 2,
    verbose: int = 1,
) -> Nifti1Image:
    """
    Generate a group EPI grey matter mask, and overlaid with a MNI grey
    matter template.
    The Group EPI mask will ensure the signal extraction is from the most
    overlapping voxels.

    Parameters
    ----------
    imgs : list of string
        List of EPI masks or preprocessed BOLD data.

    template : str, Default = MNI152NLin2009cAsym
        Template name from TemplateFlow to retrieve the grey matter template.
        This template should match the template for the EPI mask.

    templateflow_dir : None or pathlib.Path
        TemplateFlow directory. Default to None to download the directory,
        otherwise use the templateflow data saved at the given path.

    n_iter: int, optional, Default = 2
        Number of repetitions of dilation and erosion steps performed in
        scipy.ndimage.binary_closing function.

    verbose :
        Level of verbosity.

    Keyword Arguments
    -----------------
    Used to filter the cirret
    See keyword arguments in templateflow.api module.

    Return
    ------

    nibabel.nifti1.Nifti1Image
        EPI (grey matter) mask for the current group of subjects.
    """
    if verbose > 1:
        print(f"Found {len(imgs)} masks")
    if exclude := _check_mask_affine(imgs, verbose):
        imgs, __annotations__ = _get_consistent_masks(imgs, exclude)
        if verbose > 1:
            print(f"Remaining: {len(imgs)} masks")

    # templateflow environment setting to get around network issue
    if templateflow_dir and templateflow_dir.exists():
        os.environ["TEMPLATEFLOW_HOME"] = str(templateflow_dir.resolve())
    import templateflow

    # use default nilearn parameters to create the group epi mask
    group_epi_mask = compute_multi_epi_mask(
        imgs,
        lower_cutoff=0.2,
        upper_cutoff=0.85,
        connected=True,
        opening=False,  # we should be using fMRIPrep masks
        threshold=0.5,
        target_affine=None,
        target_shape=None,
        exclude_zeros=False,
        n_jobs=1,
        memory=None,
        verbose=0,
    )
    print(
        f"Group EPI mask affine:\n{group_epi_mask.affine}"
        f"\nshape: {group_epi_mask.shape}"
    )

    # load grey matter mask
    check_valid_template = re.match(r"MNI152NLin2009[ac][A]?[sS]ym", template)
    if not check_valid_template:
        raise ValueError(
            f"TemplateFlow does not supply template {template} "
            "with grey matter masks. Possible templates: "
            "MNI152NLin2009a*, MNI152NLin2009c*."
        )
    # preprocessed data don't need high res
    # for MNI152NLin2009a* templates, only one resolution is available
    gm_res = "02" if template == "MNI152NLin2009cAsym" else "1"

    mni_gm_path = templateflow.api.get(
        template,
        raise_empty=True,
        label="GM",
        resolution=gm_res,
    )

    mni_gm = resample_to_img(
        source_img=mni_gm_path,
        target_img=group_epi_mask,
        interpolation="continuous",
    )
    # the following steps are take from
    # nilearn.images.fetch_icbm152_brain_gm_mask
    mni_gm_data = get_data(mni_gm)
    # this is a probalistic mask, getting one fifth of the values
    mni_gm_mask = (mni_gm_data > 0.2).astype("int8")
    mni_gm_mask = binary_closing(mni_gm_mask, iterations=n_iter)
    mni_gm_mask_img = new_img_like(mni_gm, mni_gm_mask)

    # now we combine both masks into one
    return math_img("img1 & img2", img1=group_epi_mask, img2=mni_gm_mask_img)


def load_atlas_setting(atlas: Union[str, Path, dict]):
    """
    Load atlas details for templateflow api to fetch.
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
    atlas_config = _load_config(atlas)
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


def _load_config(atlas: Union[str, Path, dict]) -> dict:
    """Load the configuration file."""
    if isinstance(atlas, (str, Path)):
        if atlas in PRESET_ATLAS:
            config_path = resource_filename(
                "giga_connectome", f"data/atlas/{atlas}.json"
            )
        elif Path(atlas).exists():
            config_path = Path(atlas)

        with open(config_path, "r") as file:
            atlas_config = json.load(file)
    elif isinstance(atlas, dict):
        if "parameters" in atlas:
            atlas_config = atlas.copy()
        else:
            raise ValueError(
                "Invalid dictionary input. Input should"
                " contain the following keys: 'name', "
                "'parameters', 'templateflow_dir'. Found "
                f"{list(atlas.keys())}"
            )
    else:
        raise ValueError(f"Invalid input: {atlas}")
    return atlas_config


def _get_consistent_masks(
    mask_imgs: List[Union[Path, str, Nifti1Image]], exclude: List[int]
) -> Tuple[List[int], List[str]]:
    """Create a list of masks that has the same affine.

    Parameters
    ----------

    mask_imgs :
        The original list of functional masks

    exclude :
        List of index to exclude.

    Returns
    -------
    List of str
        Functional masks with the same affine.

    List of str
        Identidiers of scans with a different affine.
    """
    weird_mask_identifiers = []
    odd_masks = np.array(mask_imgs)[np.array(exclude)]
    odd_masks = odd_masks.tolist()
    for odd_file in odd_masks:
        identifier = Path(odd_file).name.split("_space")[0]
        weird_mask_identifiers.append(identifier)
    cleaned_func_masks = set(mask_imgs) - set(odd_masks)
    cleaned_func_masks = list(cleaned_func_masks)
    return cleaned_func_masks, weird_mask_identifiers


def _check_mask_affine(
    mask_imgs: List[Union[Path, str, Nifti1Image]], verbose: int = 1
) -> Union[list, None]:
    """Given a list of input mask images, show the most common affine matrix
    and subjects with different values.

    Parameters
    ----------
    mask_imgs : :obj:`list` of Niimg-like objects
        See :ref:`extracting_data`.
        3D or 4D EPI image with same affine.

    verbose :
        Level of verbosity.

    Returns
    -------

    List or None
        Index of masks with odd affine matrix. Return None when all masks have
        the same affine matrix.
    """
    # save all header and affine info in hashable type...
    header_info = {"affine": []}
    key_to_header = {}
    for this_mask in mask_imgs:
        img = load_img(this_mask)
        affine = img.affine
        affine_hashable = str(affine)
        header_info["affine"].append(affine_hashable)
        if affine_hashable not in key_to_header:
            key_to_header[affine_hashable] = affine

    if isinstance(mask_imgs[0], Nifti1Image):
        mask_imgs = np.arange(len(mask_imgs))
    else:
        mask_imgs = np.array(mask_imgs)
    # get most common values
    common_affine = max(
        set(header_info["affine"]), key=header_info["affine"].count
    )
    if verbose > 0:
        print(
            f"We found {len(set(header_info['affine']))} unique affine "
            f"matrices. The most common one is "
            f"{key_to_header[common_affine]}"
        )
    odd_balls = set(header_info["affine"]) - {common_affine}
    if not odd_balls:
        return None

    exclude = []
    for ob in odd_balls:
        ob_index = [
            i for i, aff in enumerate(header_info["affine"]) if aff == ob
        ]
        if verbose > 1:
            print(
                "The following subjects has a different affine matrix "
                f"({key_to_header[ob]}) comparing to the most common value: "
                f"{mask_imgs[ob_index]}."
            )
        exclude += ob_index
    if verbose > 0:
        print(
            f"{len(exclude)} out of {len(mask_imgs)} has "
            "different affine matrix. Ignore when creating group mask."
        )
    return sorted(exclude)
