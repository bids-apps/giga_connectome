from typing import List
from pathlib import Path
from nilearn.interfaces.bids import parse_bids_filename
from bids.layout import Query
from bids import BIDSLayout


def get_bids_images(subjects, template, bids_dir, reindex_bids, bids_filters):
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
        "space": template,
        "task": Query.ANY,
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
    for suffix, entities in bids_filters.items():
        queries[suffix].update(entities)
        for entity in list(layout_get_kwargs.keys()):
            if entity in entities:
                # avoid clobbering layout.get
                del layout_get_kwargs[entity]

    subj_data = {
        dtype: layout.get(**layout_get_kwargs, **query)
        for dtype, query in queries.items()
    }
    return subj_data, layout


def check_filter(bids_filters):
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


def _filter_pybids_none_any(dct):
    import bids

    return {
        k: bids.layout.Query.NONE
        if v is None
        else (bids.layout.Query.ANY if v == "*" else v)
        for k, v in dct.items()
    }


def parse_bids_filter(value):
    from json import JSONDecodeError, loads

    if value:
        if Path(value).exists():
            try:
                return loads(
                    Path(value).read_text(),
                    object_hook=_filter_pybids_none_any,
                )
            except JSONDecodeError:
                raise JSONDecodeError(f"JSON syntax error in: <{value}>.")
        else:
            raise FileNotFoundError(f"Path does not exist: <{value}>.")


def parse_standardize_options(standardize):
    if standardize not in ["zscore", "psc"]:
        raise ValueError(f"{standardize} is no valid standardize strategy.")
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
