import os
import re
from typing import Optional, Union, List, Tuple
from bids.layout import BIDSImageFile

from pathlib import Path
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

from giga_connectome.atlas import resample_atlas_collection

from giga_connectome.logger import gc_logger

gc_log = gc_logger()


def generate_gm_mask_atlas(
    working_dir: Path,
    atlas: dict,
    template: str,
    masks: List[BIDSImageFile],
) -> Tuple[Path, List[Path]]:
    """ """
    # check masks; isolate this part and make sure to make it a validate
    # templateflow template with a config file

    group_mask_dir = working_dir / "groupmasks" / f"tpl-{template}"
    group_mask_dir.mkdir(exist_ok=True, parents=True)

    group_mask, resampled_atlases = None, None
    if group_mask_dir.exists():
        group_mask, resampled_atlases = _check_pregenerated_masks(
            template, working_dir, atlas
        )

    if not group_mask:
        # grey matter group mask is only supplied in MNI152NLin2009c(A)sym
        group_mask_nii = generate_group_mask(
            [m.path for m in masks], "MNI152NLin2009cAsym"
        )
        current_file_name = (
            f"tpl-{template}_res-dataset_label-GM_desc-group_mask.nii.gz"
        )
        group_mask = group_mask_dir / current_file_name
        nib.save(group_mask_nii, group_mask)

    if not resampled_atlases:
        resampled_atlases = resample_atlas_collection(
            template, atlas, group_mask_dir, group_mask
        )

    return group_mask, resampled_atlases


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
    gc_log.debug(f"Found {len(imgs)} masks")
    if exclude := _check_mask_affine(imgs):
        imgs, __annotations__ = _get_consistent_masks(imgs, exclude)
        gc_log.debug(f"Remaining: {len(imgs)} masks")

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
    gc_log.info(
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
    mask_imgs: List[Union[Path, str, Nifti1Image]]
) -> Union[list, None]:
    """Given a list of input mask images, show the most common affine matrix
    and subjects with different values.

    Parameters
    ----------
    mask_imgs : :obj:`list` of Niimg-like objects
        See :ref:`extracting_data`.
        3D or 4D EPI image with same affine.

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
    gc_log.info(
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
        gc_log.debug(
            "The following subjects has a different affine matrix "
            f"({key_to_header[ob]}) comparing to the most common value: "
            f"{mask_imgs[ob_index]}."
        )
        exclude += ob_index
    gc_log.info(
        f"{len(exclude)} out of {len(mask_imgs)} has "
        "different affine matrix. Ignore when creating group mask."
    )
    return sorted(exclude)


def _check_pregenerated_masks(template, working_dir, atlas):
    """Check if the working directory is populated with needed files."""
    output_dir = working_dir / "groupmasks" / f"tpl-{template}"
    group_mask = (
        output_dir
        / f"tpl-{template}_res-dataset_label-GM_desc-group_mask.nii.gz"
    )
    if not group_mask.exists():
        group_mask = None
    else:
        gc_log.info(
            f"Found pregenerated group level grey matter mask: {group_mask}"
        )

    # atlas
    resampled_atlases = []
    for desc in atlas["file_paths"]:
        filename = (
            f"tpl-{template}_"
            f"atlas-{atlas['name']}_"
            "res-dataset_"
            f"desc-{desc}_"
            f"{atlas['type']}.nii.gz"
        )
        resampled_atlases.append(output_dir / filename)
    all_exist = [file_path.exists() for file_path in resampled_atlases]
    if not all(all_exist):
        resampled_atlases = None
    else:
        gc_log.info(
            f"Found resampled atlases:\n{[str(x) for x in resampled_atlases]}."
            "\nSkipping group level mask generation step."
        )
    return group_mask, resampled_atlases
