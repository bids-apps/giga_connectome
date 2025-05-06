from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bids import BIDSLayout
from bids.layout import BIDSFile, Query
from nilearn.interfaces.bids import parse_bids_filename
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from giga_connectome import __version__
from giga_connectome.logger import gc_logger
from giga_connectome.denoise import is_ica_aroma, STRATEGY_TYPE


gc_log = gc_logger()


def prepare_bidsfilter_and_template(
    strategy: STRATEGY_TYPE,
    user_bids_filter: None | dict[str, dict[str, str]],
) -> tuple[str, dict[str, dict[str, str]]]:
    """
    Prepare the template and BIDS filters for ICA AROMA.
    This solution only applies to fMRIPrep version < 23.1.0.
    For later versions, we will wait for updates in the upstream library
    nilearn to support the new layoput for ICA AROMA.

    Parameters
    ----------
    strategy : str
        The denoising strategy.
    bids_filter_file : Path
        The path to the BIDS filter file.

    Returns
    -------
    tuple[str, None | dict[str, dict[str, str]]]
        The template and BIDS filters.
    """
    user_bids_filter = check_filter(user_bids_filter)
    if is_ica_aroma(strategy):
        template = "MNI152NLin6Asym"
        bids_filters = {  # this only applies to fMRIPrep version < 23.1.0
            "bold": {
                "desc": "smoothAROMAnonaggr",
                "space": "MNI152NLin6Asym",
            },
            "mask": {  # no brain mask for MNI152NLin6Asym, use the closest
                "space": "MNI152NLin2009cAsym",
            },
        }
        if user_bids_filter:
            for suffix, entities in user_bids_filter.items():
                bids_filters[suffix].update(entities)
        return template, bids_filters
    else:
        return "MNI152NLin2009cAsym", user_bids_filter


def get_bids_images(
    subjects: list[str],
    template: str,
    bids_dir: Path,
    reindex_bids: bool,
    bids_filters: None | dict[str, dict[str, str]],
) -> tuple[dict[str, list[BIDSFile]], BIDSLayout]:
    """
    Apply BIDS filter to the base filter we are using.
    Modified from fmripprep
    """

    bids_filters = check_filter(bids_filters)

    layout = BIDSLayout(
        root=bids_dir,
        database_path=bids_dir,
        validate=False,
        derivatives=False,
        reset_database=reindex_bids,
        config=["bids", "derivatives"],
    )

    layout_get_kwargs = {
        "return_type": "object",
        "subject": subjects,
        "session": Query.OPTIONAL,
        "task": Query.ANY,
        "run": Query.OPTIONAL,
        "extension": ".nii.gz",
    }
    queries = {
        "bold": {
            "desc": "preproc",
            "space": template,
            "suffix": "bold",
            "datatype": "func",
        },
        "mask": {
            "suffix": "mask",
            "space": "MNI152NLin2009cAsym",
            "datatype": "func",
        },
    }

    # update individual queries first
    for suffix, entities in bids_filters.items():
        queries[suffix].update(entities)

    # now go through the shared entities in layout_get_kwargs
    for entity in list(layout_get_kwargs.keys()):
        for suffix, entities in bids_filters.items():
            if entity in entities:
                # avoid clobbering layout.get
                layout_get_kwargs.update({entity: entities[entity]})
                del queries[suffix][entity]

    subj_data = {
        dtype: layout.get(**layout_get_kwargs, **query)
        for dtype, query in queries.items()
    }
    return subj_data, layout


def check_filter(
    bids_filters: None | dict[str, dict[str, str]],
) -> dict[str, dict[str, str]]:
    """Should only have bold and mask."""
    if not bids_filters:
        return {}
    queries = list(bids_filters.keys())
    base = ["bold", "mask"]
    all_detected = set(base).union(set(queries))
    if len(all_detected) > len(base):
        extra = all_detected.difference(set(base))
        raise ValueError(
            "The only meaningful filters for giga-connectome are 'bold' "
            f"and 'mask'. We found other filters here: {extra}."
        )
    return bids_filters


def _filter_pybids_none_any(
    dct: dict[str, None | str],
) -> dict[str, Query.NONE | Query.ANY]:
    return {
        k: Query.NONE if v is None else (Query.ANY if v == "*" else v)
        for k, v in dct.items()
    }


def parse_bids_filter(value: Path) -> None | dict[str, dict[str, str]]:
    """Parse a BIDS filter json file.
    Parameters
    ----------
    value : Path
        Path to the BIDS json file.

    Returns
    -------
    dict
        Dictionary of BIDS filters.
    """

    from json import JSONDecodeError, loads

    if not value:
        return None

    if not value.exists():
        raise FileNotFoundError(f"Path does not exist: <{value}>.")
    try:
        tmp = loads(
            value.read_text(),
            object_hook=_filter_pybids_none_any,
        )
    except JSONDecodeError as e:
        raise ValueError(f"JSON syntax error in: <{value}>.") from e
    return tmp


def parse_bids_name(img: str) -> tuple[str, str | None, str]:
    """Get subject, session, and specifier for a fMRIPrep output."""
    reference = parse_bids_filename(img)

    subject = f"sub-{reference['sub']}"

    specifier = f"task-{reference['task']}"
    run = reference.get("run", None)
    if isinstance(run, str):
        specifier = f"{specifier}_run-{run}"

    session = reference.get("ses", None)
    if isinstance(session, str):
        session = f"ses-{session}"
        specifier = f"{session}_{specifier}"

    return subject, session, specifier


def get_subject_lists(
    participant_label: None | list[str] = None, bids_dir: None | Path = None
) -> list[str]:
    """
    Parse subject list from user options.

    Parameters
    ----------

    participant_label :

        A list of BIDS competible subject identifiers.
        If the prefix `sub-` is present, it will be removed.

    bids_dir :

        The fMRIPrep derivative output.

    Return
    ------

    list
        BIDS subject identifier without `sub-` prefix.
    """
    if participant_label:
        # TODO: check these IDs exists
        checked_labels = []
        for sub_id in participant_label:
            if "sub-" in sub_id:
                sub_id = sub_id.replace("sub-", "")
            checked_labels.append(sub_id)
        return checked_labels
    # get all subjects, this is quicker than bids...
    if bids_dir:
        subject_dirs = bids_dir.glob("sub-*/")
        return [
            subject_dir.name.split("-")[-1]
            for subject_dir in subject_dirs
            if subject_dir.is_dir()
        ]
    return []


def check_path(path: Path) -> None:
    """Check if given path (file or dir) already exists.

    If so, a warning is logged and the previous file is deleted.
    If the parent path does not exist, it is created.
    """
    path = path.absolute()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        gc_log.warning(
            f"Specified path already exists:\n\t{path}\n"
            "Old file will be overwritten."
        )
        path.unlink()


def create_ds_description(output_dir: Path) -> None:
    """Create a dataset_description.json file."""
    ds_desc: dict[str, Any] = {
        "BIDSVersion": "1.9.0",
        "License": None,
        "Name": None,
        "ReferencesAndLinks": [],
        "DatasetDOI": None,
        "DatasetType": "derivative",
        "GeneratedBy": [
            {
                "Name": "giga_connectome",
                "Version": __version__,
                "CodeURL": "https://github.com/bids-apps/giga_connectome.git",
            }
        ],
        "HowToAcknowledge": (
            "Please refer to our repository: "
            "https://github.com/bids-apps/giga_connectome.git."
        ),
    }
    with open(output_dir / "dataset_description.json", "w") as f:
        json.dump(ds_desc, f, indent=4)


def create_sidecar(output_path: Path) -> None:
    """Create a JSON sidecar for the connectivity data."""
    metadata: dict[str, Any] = {
        "Measure": "Pearson correlation",
        "MeasureDescription": "Pearson correlation",
        "Weighted": False,
        "Directed": False,
        "ValidDiagonal": True,
        "StorageFormat": "Full",
        "NonNegative": "",
        "Code": "https://github.com/bids-apps/giga_connectome.git",
    }
    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=4)


def output_filename(
    source_file: str,
    atlas: str,
    suffix: str,
    extension: str,
    strategy: str | None = None,
    atlas_desc: str | None = None,
) -> str:
    """Generate output filneme."""
    subject, session, specifier = parse_bids_name(source_file)
    seg = f"seg-{atlas}{atlas_desc}"
    if extension != "nii.gz":
        root: str = f"{subject}_{specifier}"

        if extension != "json":
            root += f"_{seg}"

        if suffix == "relmat":
            root += "_meas-PearsonCorrelation"

        if strategy is None:
            strategy = ""

        return (
            f"{root}_desc-denoise{strategy.capitalize()}_{suffix}.{extension}"
        )

    elif suffix == "mask":
        reference = parse_bids_filename(source_file)
        tpl: str = f"space-{reference['space']}"
        tpl += f"_res-{reference['res']}" if "res" in reference else ""
        return f"{subject}_{tpl}_label-GM_{suffix}.{extension}"
    else:
        return f"{subject}_{seg}_{suffix}.{extension}"


def progress_bar(text: str, color: str = "green") -> Progress:
    return Progress(
        TextColumn(f"[{color}]{text}"),
        SpinnerColumn("dots"),
        TimeElapsedColumn(),
        BarColumn(),
        MofNCompleteColumn(),
        TaskProgressColumn(),
        TimeRemainingColumn(),
    )
