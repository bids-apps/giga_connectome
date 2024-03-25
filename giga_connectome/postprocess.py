from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd
from bids.layout import BIDSImageFile
from nilearn.connectome import ConnectivityMeasure
from nilearn.maskers import NiftiLabelsMasker, NiftiMapsMasker

from giga_connectome import utils
from giga_connectome.atlas import ATLAS_SETTING_TYPE
from giga_connectome.connectome import generate_timeseries_connectomes
from giga_connectome.denoise import STRATEGY_TYPE, denoise_nifti_voxel
from giga_connectome.logger import gc_logger
from giga_connectome.utils import progress_bar

gc_log = gc_logger()


def run_postprocessing_dataset(
    strategy: STRATEGY_TYPE,
    atlas: ATLAS_SETTING_TYPE,
    resampled_atlases: Sequence[str | Path],
    images: Sequence[BIDSImageFile],
    group_mask: str | Path,
    standardize: bool,
    smoothing_fwhm: float,
    output_path: Path,
    calculate_average_correlation: bool = False,
) -> None:
    """
    Generate subject and group level timeseries and connectomes.

    The time series data is denoised as follow:

    - Time series extractions through label or map maskers are performed \
        on the denoised nifti file. Denoising steps are performed on the \
        voxel level:

        - spatial smoothing

        - detrend, only if high pass filter is not applied through confounds

        - Regress out confounds

        - standardize

    - Extract time series from atlas

    - Compute correlation matrix

    - Optional: average correlation within each parcel.

    - Save timeseries and correlation matrix to h5 file

    - Optional: Create average correlation matrix across subjects when using \
        group level analysis.

    Parameters
    ----------

    strategy : dict
        Parameters for `load_confounds_strategy` or `load_confounds`.

    atlas : dict
        Atlas settings.

    resampled_atlases : list of str or pathlib.Path
        Atlas niftis resampled to the common space of the dataset.

    images : list of BIDSImageFile
        Preprocessed Nifti images for post processing

    group_mask : str or pathlib.Path
        Group level grey matter mask.

    standardize : bool
        Standardization to zscore or not used in nilearn, passed to nilearn \
            masker.

    smoothing_fwhm : float
        Smoothing kernel size, passed to nilearn masker.

    output_path:
        Full path to output directory.

    analysis_level : str
        Level of analysis, only "participant" is available.

    calculate_average_correlation : bool
        Whether to calculate average correlation within each parcel.
    """
    atlas_maskers: dict[str, (NiftiLabelsMasker | NiftiMapsMasker)] = {}
    connectomes: dict[str, list[np.ndarray[Any, Any]]] = {}
    for atlas_path in resampled_atlases:
        if isinstance(atlas_path, str):
            atlas_path = Path(atlas_path)
        desc = atlas_path.name.split("desc-")[-1].split("_")[0]
        atlas_maskers[desc] = _get_masker(atlas_path)
        connectomes[desc] = []

    correlation_measure = ConnectivityMeasure(
        kind="correlation", vectorize=False, discard_diagonal=False
    )

    # transform data
    gc_log.info("Processing subject")

    with progress_bar(text="Processing subject") as progress:
        task = progress.add_task(
            description="processing subject", total=len(images)
        )

        for img in images:
            print()
            gc_log.info(f"Processing image:\n{img.filename}")

            # process timeseries
            denoised_img = denoise_nifti_voxel(
                strategy, group_mask, standardize, smoothing_fwhm, img.path
            )
            # parse file name
            subject, session, specifier = utils.parse_bids_name(img.path)

            # folder for this subject output
            connectome_path = output_path / subject
            if session:
                connectome_path = connectome_path / session
            connectome_path = connectome_path / "func"

            # All timeseries derivatives have the same metadata
            # so one json file for them all.
            # see https://bids.neuroimaging.io/bep012
            json_filename = connectome_path / utils.output_filename(
                source_file=Path(img.filename).stem,
                atlas=atlas["name"],
                suffix="timeseries",
                extension="json",
            )
            utils.check_path(json_filename)
            with open(json_filename, "w") as f:
                json.dump(
                    {"SamplingFrequency": 1 / img.entities["RepetitionTime"]},
                    f,
                    indent=4,
                )

            for desc, masker in atlas_maskers.items():

                if not denoised_img:
                    time_series_atlas, correlation_matrix = None, None
                    attribute_name = (
                        f"{subject}_{specifier}"
                        f"_atlas-{atlas['name']}_desc-{desc}"
                    )
                    gc_log.info(f"{attribute_name}: no volume after scrubbing")
                    progress.update(task, advance=1)
                    continue

                # extract timeseries and connectomes
                (correlation_matrix, time_series_atlas, masker) = (
                    generate_timeseries_connectomes(
                        masker,
                        denoised_img,
                        group_mask,
                        correlation_measure,
                        calculate_average_correlation,
                    )
                )

                # dump correlation_matrix to tsv
                relmat_filename = connectome_path / utils.output_filename(
                    source_file=Path(img.filename).stem,
                    atlas=atlas["name"],
                    suffix="relmat",
                    extension="tsv",
                    strategy=strategy["name"],
                    desc=desc,
                )
                utils.check_path(relmat_filename)
                df = pd.DataFrame(correlation_matrix)
                df.to_csv(relmat_filename, sep="\t", index=False)

                # dump timeseries to tsv file
                timeseries_filename = connectome_path / utils.output_filename(
                    source_file=Path(img.filename).stem,
                    atlas=atlas["name"],
                    suffix="timeseries",
                    extension="tsv",
                    strategy=strategy["name"],
                    desc=desc,
                )
                utils.check_path(timeseries_filename)
                df = pd.DataFrame(time_series_atlas)
                df.to_csv(timeseries_filename, sep="\t", index=False)

                report = masker.generate_report()
                report_filename = connectome_path / utils.output_filename(
                    source_file=Path(img.filename).stem,
                    atlas=atlas["name"],
                    suffix="report",
                    extension="html",
                    strategy=strategy["name"],
                    desc=desc,
                )
                report.save_as_html(report_filename)

            progress.update(task, advance=1)

    gc_log.info(f"Saved to:\n{connectome_path}")


def _get_masker(atlas_path: Path) -> NiftiLabelsMasker | NiftiMapsMasker:
    """Get the masker object based on the templateflow file name suffix."""
    atlas_type = atlas_path.name.split("_")[-1].split(".nii")[0]
    if atlas_type == "dseg":
        atlas_masker = NiftiLabelsMasker(
            labels_img=atlas_path,
            standardize=False,
            cmap="gray",
        )
    elif atlas_type == "probseg":
        atlas_masker = NiftiMapsMasker(
            maps_img=atlas_path,
            standardize=False,
            cmap="gray",
        )
    return atlas_masker
