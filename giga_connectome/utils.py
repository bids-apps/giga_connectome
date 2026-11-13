from __future__ import annotations

import json
import sqlite3
from contextlib import closing
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

from giga_connectome._version import __version__
from giga_connectome.denoise import STRATEGY_TYPE, is_ica_aroma
from giga_connectome.logger import gc_logger

gc_log = gc_logger()
PYBIDS_DATABASE_FILE = "layout_index.sqlite"


def prepare_bidsfilter_and_template(
    strategy: STRATEGY_TYPE,
    user_bids_filter: dict[str, dict[str, str]] | None,
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


def _pybids_database_mismatch(
    database_path: Path, bids_dir: Path
) -> str | None:
    """Explain why the PyBIDS index ``database_path`` can't be reused for
    ``bids_dir``. Return None if it can be reused, or if there is no index.

    PyBIDS silently replaces the ``root`` and ``config`` arguments with the
    values stored in an existing index, so a mismatch has to be caught here.
    """
    if not database_path.exists():
        return None
    try:
        uri = f"{database_path.resolve().as_uri()}?mode=ro"
        with closing(sqlite3.connect(uri, uri=True)) as conn:
            stored_root, stored_config = conn.execute(
                "SELECT root, _config FROM layout_info"
            ).fetchone()
    except (sqlite3.Error, TypeError):
        return "it could not be read"

    if Path(stored_root).resolve() != Path(bids_dir).resolve():
        return f"it indexes {stored_root}, not {bids_dir}"
    if "derivatives" not in json.loads(stored_config or "[]"):
        return (
            "it was not built with the 'derivatives' config, which is "
            "needed to query fMRIPrep outputs"
        )
    return None


def select_bids_database(
    database_path: Path | None,
    bids_dir: Path,
    output_dir: Path,
    reindex_bids: bool,
) -> Path:
    """Pick the directory of the PyBIDS index to use for ``bids_dir``.

    A user supplied ``database_path`` (a ``layout_index.sqlite`` file) is
    reused if it is a PyBIDS index built for ``bids_dir`` and ``reindex_bids``
    is False, and generated there if it does not exist yet. An existing index
    is never modified: if it cannot be reused, or ``reindex_bids`` is True, a
    new index is generated at ``<output_dir>/layout_index.sqlite``, as it is
    when ``database_path`` is None.

    Returns
    -------
    Path
        The directory holding the index, as expected by PyBIDS.
    """
    default_dir = Path(output_dir)
    default_file = default_dir / PYBIDS_DATABASE_FILE
    if database_path is None:
        gc_log.info(f"Generate PyBIDS database: {default_file}")
        return default_dir

    database_path = Path(database_path)
    if database_path.is_dir():
        raise ValueError(
            f"The PyBIDS database path must be the sqlite file of {bids_dir}, "
            "not a directory."
        )
    # PyBIDS only reads and writes <directory>/layout_index.sqlite
    if database_path.name != PYBIDS_DATABASE_FILE:
        raise ValueError(
            f"The PyBIDS database file must be named "
            f"'{PYBIDS_DATABASE_FILE}', got {database_path}."
        )
    if not database_path.exists():
        gc_log.info(f"Generate PyBIDS database: {database_path}")
        return database_path.parent
    if database_path.resolve() == default_file.resolve():
        # already the default location, which is ours to rebuild
        return default_dir

    reason: str | None
    if reindex_bids:
        reason = "--reindex-bids is set"
    else:
        reason = _pybids_database_mismatch(database_path, bids_dir)
    if reason is None:
        gc_log.info(f"Reusing PyBIDS database: {database_path}")
        return database_path.parent
    gc_log.warning(
        f"Not using the PyBIDS database at {database_path} ({reason}); "
        f"it is left unchanged. Generate PyBIDS database: {default_file}"
    )
    return default_dir


def get_bids_images(
    subjects: list[str],
    template: str,
    bids_dir: Path,
    reindex_bids: bool,
    bids_filters: dict[str, dict[str, str]] | None,
    database_path: Path | None = None,
) -> tuple[dict[str, list[BIDSFile]], BIDSLayout]:
    """
    Apply BIDS filter to the base filter we are using.
    Modified from fmripprep.

    Parameters
    ----------
    database_path : Path or None
        Directory where the PyBIDS SQLite index is stored.
        If None, the index is stored in ``bids_dir``.
        Set this to a writable location when ``bids_dir`` is read-only.
        An existing index there is reused unless ``reindex_bids`` is True
        or it was not built for ``bids_dir``, in which case it is rebuilt.
    """
    bids_filters = check_filter(bids_filters)

    database_path = Path(bids_dir if database_path is None else database_path)
    database_path.mkdir(parents=True, exist_ok=True)
    if not reindex_bids:
        reason = _pybids_database_mismatch(
            database_path / PYBIDS_DATABASE_FILE, bids_dir
        )
        if reason is not None:
            gc_log.warning(
                f"Rebuilding the PyBIDS database at {database_path} "
                f"({reason})."
            )
            reindex_bids = True

    layout = BIDSLayout(
        root=bids_dir,
        database_path=database_path,
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
    bids_filters: dict[str, dict[str, str]] | None,
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
    dct: dict[str, str | None],
) -> dict[str, Query.NONE | Query.ANY]:
    return {
        k: Query.NONE if v is None else (Query.ANY if v == "*" else v)
        for k, v in dct.items()
    }


def parse_bids_filter(value: Path) -> dict[str, dict[str, str]] | None:
    """Parse a BIDS filter json file.

    Parameters.
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

    subject = f"sub-{reference['entities']['sub']}"

    specifier = f"task-{reference['entities']['task']}"
    run = reference["entities"].get("run", None)
    if isinstance(run, str):
        specifier = f"{specifier}_run-{run}"

    session = reference["entities"].get("ses", None)
    if isinstance(session, str):
        session = f"ses-{session}"
        specifier = f"{session}_{specifier}"

    return subject, session, specifier


def get_subject_lists(
    participant_label: list[str] | None = None, bids_dir: Path | None = None
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
        subject_dirs = sorted(bids_dir.glob("sub-*/"))
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
    subject, _session, specifier = parse_bids_name(source_file)
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
        tpl: str = f"space-{reference['entities']['space']}"
        tpl += (
            f"_res-{reference['entities']['res']}"
            if "res" in reference["entities"]
            else ""
        )
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
