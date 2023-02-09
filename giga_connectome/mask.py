import os
import re
import json
from typing import Optional, Union, List, Tuple

from pathlib import Path
from tqdm import tqdm
import nibabel as nib

from nilearn.masking import compute_multi_epi_mask
from nilearn.image import resample_to_img, new_img_like, get_data, math_img
from nibabel import Nifti1Image
from scipy.ndimage import binary_closing

from pkg_resources import resource_filename


def create_group_masks_atlas(
    all_masks: List[Union[str, Path]],
    template: str,
    atlas: str,
    working_dir: Path,
) -> Tuple[Path, List[Path]]:
    """
    A High level wrapper for creating group level grey matter mask and atlas.
    The grey matter mask is always sampled to the MNI152NLin2009cAsym one,
    as that's the most commonly used grey matter mask.

    Parameters
    ----------

    all_masks: list of string or pathlib.Path
        Paths of all the fMRIPrep whole brain EPI masks that should be
        included in group mask creation.

    template: str
        Templateflow template name. This template should match the template of
        `all_masks`.

    atlas: str
        Atlas name. Currently support Schaefer20187Networks, MIST, DiFuMo.

    working_dir: pathlib.Path
        Path to working directory where the outputs are saved.

    Returns
    -------

    pathlib.Path
        Path to group level grey matter mask.

    List of pathlib.Path
        Paths to atlases sampled to group level grey matter mask.
    """
    # no grey matter mask is supplied with MNI152NLin6Asym
    # so we are fixed at using the most common space from
    # fmriprep output
    group_mask = generate_group_mask(all_masks, "MNI152NLin2009cAsym")
    current_file_name = (
        f"tpl-{template}_res-dataset_label-GM_desc-group_mask.nii.gz"
    )

    group_mask_path = working_dir / current_file_name
    nib.save(group_mask, group_mask_path)

    # dataset level atlas correction
    # TODO: can implement some kinds of caching file found in working dir
    atlas_parameters = load_atlas_setting()[atlas]
    print("Resample atlas to group grey matter mask.")
    resampled_atlases = []
    for desc in tqdm(atlas_parameters["desc"]):
        parcellation_resampled = resample_atlas2groupmask(
            atlas,
            desc,
            group_mask,
        )
        filename = (
            f"tpl-{template}_"
            f"atlas-{atlas_parameters['atlas']}_"
            "res-dataset_"
            f"desc-{desc}_"
            f"{atlas_parameters['type']}.nii.gz"
        )
        save_path = working_dir / filename
        nib.save(parcellation_resampled, save_path)
        resampled_atlases.append(save_path)
    return group_mask_path, resampled_atlases


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


def resample_atlas2groupmask(
    atlas: str,
    desc: str,
    group_mask: Union[str, Path, Nifti1Image],
    templateflow_dir: Optional[Path] = None,
) -> Nifti1Image:
    """
    Resample atlas to group EPI grey matter mask.

    Parameters
    ----------

    atlas : str
        Atlas name. Currently support Schaefer20187Networks, MIST, DiFuMo.

    desc : str or int
        Description field of the atlas. Please see the set up files for
        details of each atlas.

    group_mask : str or pathlib.Path or nibabel.nifti1.Nifti1Image
        A group-level EPI grey matter mask.

    templateflow_dir : None or pathlib.Path
        TemplateFlow directory. Default to None to download the directory,
        otherwise use the templateflow data saved at the given path.

    Return
    ------

    nibabel.nifti1.Nifti1Image
        EPI (grey matter) mask for the current group of subjects.

    str
        New filename.
    """
    # verify the atlas name and desc matches the defined data
    atlas_parameters = load_atlas_setting()[atlas]
    if desc not in atlas_parameters["desc"]:
        raise ValueError(
            f"{desc} not found. Available options for atlas "
            f"'{atlas}': {atlas_parameters['desc']}"
        )

    # templateflow environment setting to get around network issue
    if templateflow_dir and templateflow_dir.exists():
        os.environ["TEMPLATEFLOW_HOME"] = str(templateflow_dir.resolve())
    import templateflow

    parcellation = templateflow.api.get(
        atlas_parameters["template"],
        raise_empty=True,
        atlas=atlas_parameters["atlas"],
        resolution=atlas_parameters["res"],
        desc=desc,
        extension="nii.gz",
    )
    parcellation_resampled = resample_to_img(
        parcellation, group_mask, interpolation="nearest"
    )
    return parcellation_resampled


def load_atlas_setting():
    """Load atlas details for templateflow to fetch."""
    file_atlas_setting = resource_filename(
        "giga_connectome", "data/atlas_meta.json"
    )
    with open(file_atlas_setting, "r") as file:
        atlas_setting = json.load(file)
    return atlas_setting
