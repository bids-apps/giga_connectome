import json
import numpy as np
import pandas as pd

from pkg_resources import resource_filename


def get_metadata(fmriprep_bids_layout, **kwargs):
    """
    Return dict metadata with participants and files information.

    Parameters
    ----------
    fmriprep_bids_layout : bids.layout.BIDSLayout
        fMRIPrep derivative BIDS layout object.

    **kwargs :
        BIDS entities subject, session, task for further filtering.

    Return
    ------

    pandas.DataFrame
        Collection of all the relevant data. Each line is a unique functional
        image, linked to associated epi mask and confound files.
    """
    extra_entities = _check_extra_entitis(kwargs)

    # first initialize the dict with images information
    all_images = _parse_fmriprep_layout(
        fmriprep_bids_layout, "images", extra_entities
    )
    metadata = pd.DataFrame()
    for image in all_images:
        entities = {
            k: [image.entities[k]]
            for k in ["datatype", "session", "subject", "task", "space"]
            if k in image.entities
        }
        entities["image"] = image.path
        entities["template"] = entities["space"]
        entities.pop("space")
        metadata = pd.concat((metadata, pd.DataFrame(entities)))
    metadata = metadata.reset_index(drop=True)

    # update information with confounds
    all_confounds = _parse_fmriprep_layout(
        fmriprep_bids_layout, "confounds", extra_entities
    )
    for confound in all_confounds:
        row_idx = _find_matched_confound_file(metadata, confound)
        metadata.loc[row_idx, ["confound"]] = confound.path

    # update information with masks
    all_masks = _parse_fmriprep_layout(
        fmriprep_bids_layout, "masks", extra_entities
    )
    for mask in all_masks:
        row_idx = _find_matched_mask_file(metadata, mask)
        metadata.loc[row_idx, ["mask"]] = mask.path

    metadata = metadata.sort_values(["template"])
    return metadata


def _check_extra_entitis(kwargs):
    """Check key word arguments contains the specified entities."""
    extra_entities = {}
    extra_entities_names = _load_bids_entities("extra_bids_entities")
    for key in extra_entities_names:
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

    if "task" in mask.entities.keys():
        row_idx = np.logical_and(
            row_idx, metadata["task"] == mask.entities["task"]
        )
    return row_idx


def _find_matched_confound_file(metadata, confound):
    """Find matched mask to each preprocessed file."""
    row_idx = np.logical_and(
        metadata["datatype"] == confound.entities["datatype"],
        metadata["subject"] == confound.entities["subject"],
    )
    if "session" in confound.entities.keys():
        row_idx = np.logical_and(
            row_idx, metadata["session"] == confound.entities["session"]
        )
    row_idx = np.logical_and(
        row_idx, metadata["task"] == confound.entities["task"]
    )
    return row_idx


def _parse_fmriprep_layout(layout, file_type, kwargs):
    """Parese relevant fMRIPrep output for quality control."""
    bids_entities = _load_bids_entities(file_type)
    bids_entities.update(kwargs)
    return layout.get(**bids_entities)


def _load_bids_entities(file_type):
    file_bids_entities = resource_filename(
        "giga_connectome", "data/bids_entities.json"
    )
    with open(file_bids_entities, "r") as file:
        bids_entities = json.load(file)
    if file_type not in bids_entities:
        raise ValueError(f"File type {file_type} is not defined.")
    return bids_entities[file_type]
