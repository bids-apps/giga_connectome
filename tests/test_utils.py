import shutil
from pathlib import Path

import pytest
from bids import BIDSLayout
from nilearn._utils.data_gen import create_fake_bids_dataset

from giga_connectome import utils
from giga_connectome.denoise import get_denoise_strategy


def test_prepare_bidsfilter_and_template() -> None:
    # regular strategy and no user bids filter
    strategy = get_denoise_strategy("simple")
    user_bids_filter = None
    template, bids_filters = utils.prepare_bidsfilter_and_template(
        strategy, user_bids_filter
    )
    assert template == "MNI152NLin2009cAsym"
    assert bids_filters == {}

    # icaaroma and no user bids filter
    strategy = get_denoise_strategy("icaaroma")
    template, bids_filters = utils.prepare_bidsfilter_and_template(
        strategy, user_bids_filter
    )
    assert template == "MNI152NLin6Asym"
    assert type(bids_filters) is dict
    assert bids_filters["bold"]["desc"] == "smoothAROMAnonaggr"
    assert bids_filters["mask"]["space"] == "MNI152NLin2009cAsym"

    # icaaroma and user bids filter
    user_bids_filter = {
        "bold": {"task": "probabilisticclassification", "run": "1"},
    }
    template, bids_filters = utils.prepare_bidsfilter_and_template(
        strategy, user_bids_filter
    )
    assert template == "MNI152NLin6Asym"
    assert type(bids_filters) is dict
    assert bids_filters["bold"]["task"] == "probabilisticclassification"
    assert bids_filters["bold"]["desc"] == "smoothAROMAnonaggr"
    assert bids_filters["mask"]["space"] == "MNI152NLin2009cAsym"


def test_get_bids_images(bids_dir, tmp_path) -> None:
    subjects = ["1"]
    template = "MNI152NLin2009cAsym"

    reindex_bids = True
    user_bids_filters = {
        "bold": {"task": "probabilisticclassification", "run": "1"},
    }  # task and run should apply to both mask and bold
    subj_data, _ = utils.get_bids_images(
        subjects,
        template,
        bids_dir,
        reindex_bids,
        user_bids_filters,
        database_path=tmp_path,
    )
    assert len(subj_data["bold"]) == len(subj_data["mask"])

    # test for icaaroma
    strategy = get_denoise_strategy("icaaroma")
    template, bids_filters = utils.prepare_bidsfilter_and_template(
        strategy, user_bids_filters
    )
    subj_data, _ = utils.get_bids_images(
        subjects,
        template,
        bids_dir,
        reindex_bids,
        bids_filters,
        database_path=tmp_path,
    )
    assert len(subj_data["bold"]) == len(subj_data["mask"])
    assert all(
        "desc-smoothAROMAnonaggr_bold.nii.gz" in img.path
        for img in subj_data["bold"]
    )


def test_check_check_filter() -> None:
    """Unit test for utils.check_filter."""
    correct_filter = {"bold": {"suffix": "bold"}}
    assert utils.check_filter(correct_filter) == correct_filter
    with pytest.raises(ValueError) as msg:
        utils.check_filter({"bold": {"suffix": "bold"}, "dseg": {"run": "1"}})
    assert "dseg" in str(msg.value)


@pytest.mark.parametrize(
    "source_file",
    [
        "sub-01_ses-ah_task-rest_run-1_space-MNIfake_res-2_desc-preproc_bold.nii.gz",
        "sub-01_ses-ah_task-rest_run-1_space-MNIfake_res-2_desc-brain_mask.nii.gz",
    ],
)
def test_parse_bids_name(source_file) -> None:
    subject, session, specifier = utils.parse_bids_name(source_file)
    assert subject == "sub-01"
    assert session == "ses-ah"
    assert specifier == "ses-ah_task-rest_run-1"


def test_get_subject_lists(bids_dir) -> None:
    # strip the sub- prefix
    subjects = utils.get_subject_lists(participant_label=["sub-01"])
    assert len(subjects) == 1
    assert subjects[0] == "01"

    subjects = utils.get_subject_lists(bids_dir=bids_dir)
    assert len(subjects) == 2
    assert subjects[0] == "1"


def test_get_subject_lists_sorted_order(tmp_path) -> None:
    """Subject directories are created out of order on disk; the returned
    list must not depend on filesystem enumeration order.
    """
    for sub_id in ["sub-10", "sub-02", "sub-01"]:
        (tmp_path / sub_id).mkdir()

    subjects = utils.get_subject_lists(bids_dir=tmp_path)

    assert subjects == ["01", "02", "10"]


@pytest.mark.parametrize(
    "suffix,extension,target",
    [
        (
            "timeseries",
            "tsv",
            "sub-01_ses-ah_task-rest_run-1_seg-fake100_desc-denoiseSimple_timeseries.tsv",
        ),
        (
            "timeseries",
            "json",
            "sub-01_ses-ah_task-rest_run-1_desc-denoiseSimple_timeseries.json",
        ),
        (
            "relmat",
            "tsv",
            "sub-01_ses-ah_task-rest_run-1_seg-fake100_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv",
        ),
        (
            "report",
            "html",
            "sub-01_ses-ah_task-rest_run-1_seg-fake100_desc-denoiseSimple_report.html",
        ),
    ],
)
def test_output_filename(suffix, extension, target) -> None:
    source_file = (
        "sub-01_ses-ah_task-rest_run-1_space-MNIfake_"
        "res-2_desc-preproc_bold.nii.gz"
    )

    generated_target = utils.output_filename(
        source_file=source_file,
        atlas="fake",
        suffix=suffix,
        extension=extension,
        strategy="simple",
        atlas_desc="100",
    )
    assert target == generated_target


@pytest.mark.parametrize(
    "source_file,atlas,atlas_desc,suffix,target",
    [
        (
            "sub-01_ses-ah_task-rest_run-1_space-MNIfake_res-2_desc-brain_mask.nii.gz",
            "fake",
            "100",
            "dseg",
            "sub-01_seg-fake100_dseg.nii.gz",
        ),
        (
            "sub-01_ses-ah_task-rest_run-1_space-MNIfake_res-2_desc-brain_mask.nii.gz",
            "",
            "",
            "mask",
            "sub-01_space-MNIfake_res-2_label-GM_mask.nii.gz",
        ),
        (
            "sub-01_ses-ah_task-rest_run-1_space-MNIfake_desc-brain_mask.nii.gz",
            "",
            "",
            "mask",
            "sub-01_space-MNIfake_label-GM_mask.nii.gz",
        ),
    ],
)
def test_output_filename_seg(
    source_file, atlas, atlas_desc, suffix, target
) -> None:
    generated_target = utils.output_filename(
        source_file=source_file,
        atlas=atlas,
        suffix=suffix,
        extension="nii.gz",
        strategy="",
        atlas_desc=atlas_desc,
    )
    assert target == generated_target


def test_desc_entity_recognised(tmp_path) -> None:
    create_fake_bids_dataset(tmp_path, n_sub=1, n_ses=1, n_runs=[1, 1])
    utils.get_bids_images(
        ["01"],
        "MNI",
        tmp_path / "bids_dataset" / "derivatives",
        reindex_bids=True,
        bids_filters=None,
    )


TEMPLATE = "MNI152NLin2009cAsym"
DATABASE_FILE = utils.PYBIDS_DATABASE_FILE


def _get_image_paths(
    bids_dir: Path, database_dir: Path, reindex_bids: bool = False
) -> dict[str, list[str]]:
    """Query sub-1 bold and mask images through the index in database_dir."""
    subj_data, layout = utils.get_bids_images(
        ["1"], TEMPLATE, bids_dir, reindex_bids, None, database_dir
    )
    assert Path(layout.root) == bids_dir.resolve()
    return {k: sorted(f.path for f in v) for k, v in subj_data.items()}


@pytest.fixture(scope="session")
def reference_database(
    bids_dir, tmp_path_factory
) -> tuple[Path, dict[str, list[str]]]:
    """A freshly built index of bids_dir and the images it returns."""
    database_dir = tmp_path_factory.mktemp("reference_db")
    images = _get_image_paths(bids_dir, database_dir, reindex_bids=True)
    assert len(images["bold"]) == len(images["mask"]) > 0
    return database_dir / DATABASE_FILE, images


@pytest.fixture
def database_file(reference_database, tmp_path) -> Path:
    """A private copy of the reference index, safe to modify."""
    database_file = tmp_path / "pybids_db" / DATABASE_FILE
    database_file.parent.mkdir()
    shutil.copy(reference_database[0], database_file)
    return database_file


@pytest.mark.parametrize(
    "case",
    ["reuse", "reindex", "default", "new", "no_derivatives", "other_root"],
)
def test_select_bids_database(
    bids_dir, reference_database, database_file, tmp_path, case
) -> None:
    """Whether the index is reused or (re)generated, it is stored at the
    expected place and returns the same images as a freshly built index.
    """
    output_dir = tmp_path / "output"
    if case not in ("reuse", "reindex"):
        database_file.unlink()
    if case in ("no_derivatives", "other_root"):
        BIDSLayout(
            bids_dir if case == "no_derivatives" else tmp_path,
            database_path=database_file.parent,
            validate=False,
            config=["bids"] if case == "no_derivatives" else None,
        )
    mtime = database_file.stat().st_mtime_ns if case == "reuse" else None
    reindex_bids = case == "reindex"

    selected = utils.select_bids_database(
        None if case == "default" else database_file,
        bids_dir,
        output_dir,
        reindex_bids,
    )
    expected_dir = output_dir if case == "default" else database_file.parent
    assert selected == expected_dir

    assert (
        _get_image_paths(bids_dir, selected, reindex_bids)
        == (reference_database[1])
    )
    assert (expected_dir / DATABASE_FILE).exists()
    if case == "default":
        assert not database_file.exists()
    else:
        assert not (output_dir / DATABASE_FILE).exists()
    if case == "reuse":
        assert database_file.stat().st_mtime_ns == mtime


def test_select_bids_database_rejects_directory(
    bids_dir, database_file, tmp_path
) -> None:
    """A directory is rejected, even one that holds a database."""
    with pytest.raises(ValueError, match="must be the sqlite file"):
        utils.select_bids_database(
            database_file.parent, bids_dir, tmp_path, False
        )
