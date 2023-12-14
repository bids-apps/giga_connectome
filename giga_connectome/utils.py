from __future__ import annotations

from typing import List, Tuple, Union, Any
import json
from pathlib import Path

from nilearn.interfaces.bids import parse_bids_filename
from bids.layout import Query
from bids import BIDSLayout

from giga_connectome import __version__


def get_bids_images(
    subjects: List[str],
    template: str,
    bids_dir: Path,
    reindex_bids: bool,
    bids_filters: dict,
) -> Tuple[dict, BIDSLayout]:
    """
    Apply BIDS filter to the base filter we are using.
    Modified from fmripprep
    """
    bids_filters = check_filter(bids_filters)

    layout = BIDSLayout(
        root=bids_dir,
        database_path=bids_dir,
        validate=False,
        derivatives=True,
        reset_database=reindex_bids,
    )

    layout_get_kwargs = {
        "return_type": "object",
        "subject": subjects,
        "session": Query.OPTIONAL,
        "space": template,
        "task": Query.ANY,
        "run": Query.OPTIONAL,
        "extension": ".nii.gz",
    }
    queries = {
        "bold": {
            "desc": "preproc",
            "suffix": "bold",
            "datatype": "func",
        },
        "mask": {
            "suffix": "mask",
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


def check_filter(bids_filters: dict) -> dict:
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


def _filter_pybids_none_any(dct: dict) -> dict:
    import bids

    return {
        k: bids.layout.Query.NONE
        if v is None
        else (bids.layout.Query.ANY if v == "*" else v)
        for k, v in dct.items()
    }


def parse_bids_filter(value: Path) -> dict:
    from json import JSONDecodeError, loads

    if value:
        if value.exists():
            try:
                return loads(
                    value.read_text(),
                    object_hook=_filter_pybids_none_any,
                )
            except JSONDecodeError:
                raise JSONDecodeError(f"JSON syntax error in: <{value}>.")
        else:
            raise FileNotFoundError(f"Path does not exist: <{value}>.")


def parse_standardize_options(standardize: str) -> Union[str, bool]:
    if standardize not in ["zscore", "psc"]:
        raise ValueError(f"{standardize} is not a valid standardize strategy.")
    if standardize == "psc":
        return standardize
    else:
        return True


def parse_bids_name(img: str) -> List[str]:
    """Get subject, session, and specifier for a fMRIPrep output."""
    reference = parse_bids_filename(img)
    subject = f"sub-{reference['sub']}"
    session = reference.get("ses", None)
    run = reference.get("run", None)
    specifier = f"task-{reference['task']}"
    if isinstance(session, str):
        session = f"ses-{session}"
        specifier = f"{session}_{specifier}"

    if isinstance(run, str):
        specifier = f"{specifier}_run-{run}"
    return subject, session, specifier


def get_subject_lists(
    participant_label: List[str] = None, bids_dir: Path = None
) -> List[str]:
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

    List
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
    subject_dirs = bids_dir.glob("sub-*/")
    return [
        subject_dir.name.split("-")[-1]
        for subject_dir in subject_dirs
        if subject_dir.is_dir()
    ]


def check_path(path: Path, verbose=True):
    """Check if given path (file or dir) already exists, and if so returns a
    new path with _<n> appended (n being the number of paths with the same name
    that exist already).
    """
    path = path.resolve()
    ext = path.suffix
    path_parent = path.parent

    path_parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        similar_paths = [
            str(p).replace(ext, "")
            for p in path_parent.glob(f"{path.stem}_*{ext}")
        ]
        existing_numbers = [
            int(p.split("_")[-1])
            for p in similar_paths
            if p.split("_")[-1].isdigit()
        ]
        n = str(max(existing_numbers) + 1) if existing_numbers else "1"
        path = path_parent / f"{path.stem}_{n}{ext}"
        if verbose:
            print(f"Specified path already exists, using {path} instead.")
    return path


def create_ds_description(output_dir: Path) -> None:
    """Create a dataset_description.json file."""
    ds_desc: dict[str, Any] = {
        "BIDSVersion": "1.9.0",
        "License": None,
        "Name": None,
        "ReferencesAndLinks": [],
        "Authors": [
            "Foo",
            "Bar",
        ],
        "DatasetDOI": None,
        "DatasetType": "derivative",
        "GeneratedBy": [
            {
                "Name": "giga_connectome",
                "Version": __version__,
                "CodeURL": "https://github.com/SIMEXP/giga_connectome.git",
            }
        ],
        "HowToAcknowledge": (
            "Please refer to our repository: "
            "https://github.com/SIMEXP/giga_connectome.git."
        ),
    }
    with open(output_dir / "dataset_description.json", "w") as f:
        json.dump(ds_desc, f, indent=4)


def create_sidecar(output_path: Path) -> None:
    """Create a JSON sidecar for the connectivity data."""
    metadata: dict[str, Any] = {
        "NodeFiles": "REQUIRED",
        "Measure": "Pearson correlation",
        "MeasureDescription": "Pearson correlation",
        "Weighted": "REQUIRED",
        "Directed": False,
        "ValidDiagonal": True,
        "StorageFormat": "Full",
        "NonNegative": "",
        "Code": "https://github.com/SIMEXP/giga_connectome.git",
    }
    with open(output_path, "w") as f:
        json.dump(metadata, f, indent=4)


def output_filename(source_file: str, atlas: str, strategy: str) -> str:
    root = source_file.split("_")[:-1]
    root = [x for x in root if "desc" not in x]
    print(root)
    root = "_".join(root)
    if len(root) > 0:
        root += "_"
    return (
        f"{root}atlas-{atlas}_meas-PearsonCorrelation_desc-{strategy}"
        "_relmat.h5"
    )
