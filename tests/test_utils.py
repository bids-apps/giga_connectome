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


def test_get_bids_images(data_dir) -> None:
    subjects = ["1"]
    template = "MNI152NLin2009cAsym"
    bids_dir = (
        data_dir
        / "test_data"
        / "ds000017-fmriprep22.0.1-downsampled-nosurface"
    )

    reindex_bids = True
    user_bids_filters = {
        "bold": {"task": "probabilisticclassification", "run": "1"},
    }  # task and run should apply to both mask and bold
    subj_data, _ = utils.get_bids_images(
        subjects, template, bids_dir, reindex_bids, user_bids_filters
    )
    assert len(subj_data["bold"]) == len(subj_data["mask"])

    # test for icaaroma
    strategy = get_denoise_strategy("icaaroma")
    template, bids_filters = utils.prepare_bidsfilter_and_template(
        strategy, user_bids_filters
    )
    print(bids_filters)
    subj_data, _ = utils.get_bids_images(
        subjects, template, bids_dir, reindex_bids, bids_filters
    )
    print(subj_data)
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


def test_get_subject_lists(data_dir) -> None:
    # strip the sub- prefix
    subjects = utils.get_subject_lists(participant_label=["sub-01"])
    assert len(subjects) == 1
    assert subjects[0] == "01"

    subjects = utils.get_subject_lists(
        bids_dir=data_dir
        / "test_data"
        / "ds000017-fmriprep22.0.1-downsampled-nosurface"
    )
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

    subjects = ["01"]
    template = "MNI"
    reindex_bids = True

    utils.get_bids_images(
        subjects,
        template,
        tmp_path / "bids_dataset" / "derivatives",
        reindex_bids,
        bids_filters=None,
    )


def test_bids_database_dir(tmp_path) -> None:
    """The PyBIDS index is written to database_path, not to bids_dir."""
    create_fake_bids_dataset(tmp_path, n_sub=1, n_ses=1, n_runs=[1, 1])
    bids_dir = tmp_path / "bids_dataset" / "derivatives"
    database_dir = tmp_path / "pybids_db"

    utils.get_bids_images(
        ["01"],
        "MNI",
        bids_dir,
        reindex_bids=True,
        bids_filters=None,
        database_path=database_dir,
    )
    assert (database_dir / "layout_index.sqlite").exists()
    assert not (bids_dir / "layout_index.sqlite").exists()


def _make_database(bids_dir, database_dir, config=("bids", "derivatives")):
    BIDSLayout(
        bids_dir,
        database_path=database_dir,
        validate=False,
        derivatives=False,
        config=list(config),
    )
    return database_dir / "layout_index.sqlite"


def test_select_bids_database_reuse(tmp_path) -> None:
    """An existing PyBIDS index built for bids_dir is reused as is."""
    create_fake_bids_dataset(tmp_path, n_sub=1, n_ses=1, n_runs=[1, 1])
    bids_dir = tmp_path / "bids_dataset" / "derivatives"
    output_dir = tmp_path / "output"
    database_file = _make_database(bids_dir, tmp_path / "pybids_db")
    mtime = database_file.stat().st_mtime_ns

    selected = utils.select_bids_database(
        database_file, bids_dir, output_dir, reindex_bids=False
    )
    assert selected == database_file.parent
    subj_data, layout = utils.get_bids_images(
        ["01"], "MNI", bids_dir, False, None, database_path=selected
    )
    assert Path(layout.root) == bids_dir.resolve()
    assert len(subj_data["bold"]) > 0
    assert database_file.stat().st_mtime_ns == mtime
    assert not (output_dir / "layout_index.sqlite").exists()


def test_select_bids_database_default(tmp_path) -> None:
    """Without a path, the index is generated in output_dir."""
    create_fake_bids_dataset(tmp_path, n_sub=1, n_ses=1, n_runs=[1, 1])
    bids_dir = tmp_path / "bids_dataset" / "derivatives"
    output_dir = tmp_path / "output"

    selected = utils.select_bids_database(None, bids_dir, output_dir, False)
    assert selected == output_dir
    utils.get_bids_images(
        ["01"], "MNI", bids_dir, False, None, database_path=selected
    )
    assert (output_dir / "layout_index.sqlite").exists()


@pytest.mark.parametrize("case", ["new", "no_derivatives", "other_root"])
def test_select_bids_database_regenerate(tmp_path, case) -> None:
    """A missing or unusable index is generated at the given path."""
    create_fake_bids_dataset(tmp_path, n_sub=1, n_ses=1, n_runs=[1, 1])
    bids_dir = tmp_path / "bids_dataset" / "derivatives"
    database_file = tmp_path / "pybids_db" / "layout_index.sqlite"
    if case == "no_derivatives":
        _make_database(bids_dir, database_file.parent, config=("bids",))
    elif case == "other_root":
        _make_database(tmp_path / "bids_dataset", database_file.parent)

    selected = utils.select_bids_database(
        database_file, bids_dir, tmp_path / "output", False
    )
    assert selected == database_file.parent
    subj_data, layout = utils.get_bids_images(
        ["01"], "MNI", bids_dir, False, None, database_path=selected
    )
    assert Path(layout.root) == bids_dir.resolve()
    assert len(subj_data["bold"]) > 0
    assert database_file.exists()


def test_select_bids_database_rejects_directory(tmp_path) -> None:
    """A directory is rejected, even one that holds a database."""
    _make_database(tmp_path, tmp_path / "pybids_db")
    with pytest.raises(ValueError, match="must be the sqlite file"):
        utils.select_bids_database(
            tmp_path / "pybids_db", tmp_path, tmp_path, False
        )
