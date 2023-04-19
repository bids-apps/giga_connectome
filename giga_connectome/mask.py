import os
import re
import json
from typing import Optional, Union, List

from pathlib import Path
from tqdm import tqdm
import nibabel as nib

from nilearn.masking import compute_multi_epi_mask
from nilearn.image import resample_to_img, new_img_like, get_data, math_img
from nibabel import Nifti1Image
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

    Keyword Arguments
    -----------------
    Used to filter the cirret
    See keyword arguments in templateflow.api module.

    Return
    ------

    nibabel.nifti1.Nifti1Image
        EPI (grey matter) mask for the current group of subjects.
    """
    # TODO: subject native space grey matter mask???

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
