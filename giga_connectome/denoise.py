import os
import re
import json

from nilearn.masking import compute_multi_epi_mask
from nilearn.image import resample_to_img, new_img_like, get_data, math_img

from scipy.ndimage import binary_closing

from pkg_resources import resource_filename


def generate_group_mask(
    imgs, template="MNI152NLin2009aAsym", templateflow_dir=None, n_iter=2
):
    """
    Generate a group EPI grey matter mask, and overlaid with a MNI grey
    matter template.
    The Group EPI mask will ensure the signal extraction is from the most
    overlapping voxels.

    Parameters
    ----------
    imgs : list of string
        List of EPI masks or preprocessed BOLD data.

    template : str
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
        opening=2,
        threshold=0.5,
        target_affine=None,
        target_shape=None,
        exclude_zeros=False,
        n_jobs=1,
        memory=None,
        verbose=0,
    )

    # load grey matter mask
    check_valid_template = re.match(r"MNI152NLin2009[abc][A]?[sS]ym", template)
    if not check_valid_template:
        raise ValueError(
            f"TemplateFlow does not supply template {template}"
            "with grey matter masks. Please use any "
            "MNI152NLin2009* templates."
        )
    mni_gm_path = templateflow.api.get(
        template,
        raise_empty=True,
        label="GM",
    )  # this is a probalistic mask, getting one fifth of the values

    mni_gm = resample_to_img(
        source_img=mni_gm_path,
        target_img=group_epi_mask,
        interpolation="continuous",
    )
    # the following steps are take from
    # nilearn.images.fetch_icbm152_brain_gm_mask
    mni_gm_data = get_data(mni_gm)
    mni_gm_mask = (mni_gm_data > 0.2).astype("int8")
    mni_gm_mask = binary_closing(mni_gm_mask, iterations=n_iter)
    mni_gm_mask_img = new_img_like(mni_gm, mni_gm_mask)

    # now we combine both masks into one
    return math_img("img1 & img2", img1=group_epi_mask, img2=mni_gm_mask_img)


def get_denoise_strategy(strategy_name):
    """
    Select denoise strategies and associated parameters.
    The strategy parameters are designed to pass to load_confounds_strategy.

    Parameter
    ---------

    strategy_name : None or str
        Default to None, returns all strategies.
        Name of the denoising strategy options:
        simple, simple+gsr, scrubbing.5, scrubbing.5+gsr,
        scrubbing.2, scrubbing.2+gsr, acompcor50, icaaroma.

    Return
    ------

    dict
        Denosing strategy parameter to pass to load_confounds_strategy.
    """
    strategy_file = resource_filename(
        "giga_connectome", "data/denoise_strategy.json"
    )
    with open(strategy_file, "r") as file:
        benchmark_strategies = json.load(file)

    if isinstance(strategy_name, str) and (
        strategy_name not in benchmark_strategies
    ):
        raise NotImplementedError(
            f"Strategy '{strategy_name}' is not implemented. Select from the"
            f"following: {[*benchmark_strategies]}"
        )

    if strategy_name is None:
        return benchmark_strategies
    return {strategy_name: benchmark_strategies[strategy_name]}
