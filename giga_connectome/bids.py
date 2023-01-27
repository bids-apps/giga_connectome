from pathlib import Path

import bids
import json
import numpy as np
import pandas as pd

from pkg_resources import resource_filename


EXTRA_BIDS_ENTITIES = ["subject", "session", "task"]


def get_metadata(fmriprep_dir, **kwargs):
    """
    Return dict metadata with participants and files information.

    Parameters
    ----------
    fmriprep_dir : str or pathlib.Path
        Path to the fmriprep output directory.

    **kwargs :
        BIDS entities subject, session, task for further filtering.

    Return
    ------

    pandas.DataFrame
        collection of all the relevant data.
    """
    extra_entities = _check_extra_entitis(kwargs)
    layout = _get_derivative_layout(fmriprep_dir)

    metadata = pd.DataFrame(
        columns=[
            "datatype",
            "image",
            "mask",
            "confound",
            "session",
            "subject",
            "task",
            "template",
        ]
    )

    # first initialize the dict with images information
    all_images = _parse_fmriprep_layout(layout, "images", extra_entities)
    for image in all_images:
        entities = {
            k: [image.entities[k]]
            for k in ["datatype", "session", "subject", "task", "space"]
            if k in image.entities
        }
        entities["image"] = image.path
        entities["template"] = entities["space"]
        entities.pop("space")
        metadata = metadata.append(pd.DataFrame(entities))
    metadata = metadata.reset_index(drop=True)

    # update information with confounds
    all_confounds = _parse_fmriprep_layout(layout, "confounds", extra_entities)
    for confound in all_confounds:
        row_idx = _find_matched_confound_file(metadata, confound)
        metadata.at[row_idx, ["confound"]] = confound.path

    # update information with masks
    all_masks = _parse_fmriprep_layout(layout, "masks", extra_entities)
    for mask in all_masks:
        row_idx = _find_matched_mask_file(metadata, mask)
        metadata.at[row_idx, ["mask"]] = mask.path
    return metadata


def _check_extra_entitis(kwargs):
    """Check key word arguments contains only subject, session, task."""
    extra_entities = {}

    for key in EXTRA_BIDS_ENTITIES:
        value = kwargs.pop(key, None)  # get user input
        if value is not None:
            extra_entities[key] = value
    invalid_entities = list(kwargs.keys())
    if invalid_entities:
        raise UserWarning(
            f"The following BIDS entities are not used: {invalid_entities}."
        )
    return extra_entities


def _find_matched_mask_file(metadata, mask):
    """Find matched mask to each preprocessed file."""
    row_idx = np.logical_and(
        metadata["datatype"] == mask.entities["datatype"],
        metadata["subject"] == mask.entities["subject"],
    )
    row_idx = np.logical_and(
        row_idx, metadata["template"] == mask.entities["space"]
    )
    if "session" in mask.entities.keys():
        row_idx = np.logical_and(
            row_idx, metadata["session"] == mask.entities["session"]
        )
    else:
        row_idx = np.logical_and(row_idx, metadata["session"].isna())
    if "task" in mask.entities.keys():
        row_idx = np.logical_and(
            row_idx, metadata["task"] == mask.entities["task"]
        )
    else:
        row_idx = np.logical_and(row_idx, metadata["task"].isna())
    return row_idx


def _find_matched_confound_file(metadata, confound):
    """Find matched mask to each preprocessed file."""
    row_idx = np.logical_and(
        metadata["datatype"] == confound.entities["datatype"],
        metadata["session"] == confound.entities["session"],
    )
    row_idx = np.logical_and(
        row_idx, metadata["subject"] == confound.entities["subject"]
    )
    row_idx = np.logical_and(
        row_idx, metadata["task"] == confound.entities["task"]
    )
    return row_idx


def _parse_fmriprep_layout(layout, file_type, kwargs):
    """Parese relevant fMRIPrep output for quality control."""
    if file_type not in _load_bids_entities():
        raise ValueError(f"File type {file_type} is not defined.")

    target_entities = _load_bids_entities()[file_type]
    target_entities.update(kwargs)
    return layout.get(target_entities)


def _load_bids_entities():
    """Load the bids entities defined for this project."""
    file_bids_entities = resource_filename(
        "giga_connectome", "data/bids_entities.json"
    )
    with open(file_bids_entities, "r") as file:
        bids_entities = json.load(file)
    return bids_entities


def _get_derivative_layout(fmriprep_dir):
    """Get BIDS fMRIPrep derivative layout."""
    if isinstance(fmriprep_dir, str):
        fmriprep_dir = Path(fmriprep_dir)

    if not fmriprep_dir.exists():
        raise ValueError(f"Directory {fmriprep_dir} does not exists!")

    layout = bids.BIDSLayout(fmriprep_dir, validate=False)
    layout.add_derivatives(fmriprep_dir)
    return layout
