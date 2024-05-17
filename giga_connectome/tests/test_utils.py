from pathlib import Path

import pytest
from bids.tests import get_test_data_path
from pkg_resources import resource_filename

from giga_connectome import utils


def test_get_bids_images():
    subjects = ["1"]
    template = "MNI152NLin2009cAsym"
    bids_dir = resource_filename(
        "giga_connectome",
        "data/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface",
    )
    reindex_bids = True
    bids_filters = {
        "bold": {"task": "probabilisticclassification", "run": "1"},
    }  # task and run should apply to both mask and bold
    subj_data, _ = utils.get_bids_images(
        subjects, template, bids_dir, reindex_bids, bids_filters
    )
    assert len(subj_data["bold"]) == len(subj_data["mask"])


def test_check_check_filter():
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
def test_parse_bids_name(source_file):
    subject, session, specifier = utils.parse_bids_name(source_file)
    assert subject == "sub-01"
    assert session == "ses-ah"
    assert specifier == "ses-ah_task-rest_run-1"


def test_get_subject_lists():
    bids_test = Path(get_test_data_path())
    # strip the sub- prefix
    subjects = utils.get_subject_lists(participant_label=["sub-01"])
    assert len(subjects) == 1
    assert subjects[0] == "01"
    subjects = utils.get_subject_lists(
        participant_label=None, bids_dir=bids_test / "ds005_derivs/dummy"
    )
    assert len(subjects) == 1
    assert subjects[0] == "01"


def test_output_filename():
    source_file = "sub-01_ses-ah_task-rest_run-1_space-MNIfake_res-2_desc-preproc_bold.nii.gz"
    atlas = "fake"
    atlas_desc = "100"
    strategy = "simple"

    generated_target = utils.output_filename(
        source_file=source_file,
        atlas=atlas,
        suffix="timeseries",
        extension="tsv",
        strategy=strategy,
        atlas_desc=atlas_desc,
    )
    assert (
        "sub-01_ses-ah_task-rest_run-1_seg-fake100_desc-denoiseSimple_timeseries.tsv"
        == generated_target
    )

    generated_target = utils.output_filename(
        source_file=source_file,
        atlas=atlas,
        suffix="timeseries",
        extension="json",
        strategy=strategy,
        atlas_desc=atlas_desc,
    )
    assert (
        "sub-01_ses-ah_task-rest_run-1_desc-denoiseSimple_timeseries.json"
        == generated_target
    )

    generated_target = utils.output_filename(
        source_file=source_file,
        atlas=atlas,
        suffix="relmat",
        extension="tsv",
        strategy=strategy,
        atlas_desc=atlas_desc,
    )
    assert (
        "sub-01_ses-ah_task-rest_run-1_seg-fake100_meas-PearsonCorrelation_desc-denoiseSimple_relmat.tsv"
        == generated_target
    )

    generated_target = utils.output_filename(
        source_file=source_file,
        atlas=atlas,
        suffix="report",
        extension="html",
        strategy=strategy,
        atlas_desc=atlas_desc,
    )
    assert (
        "sub-01_ses-ah_task-rest_run-1_seg-fake100_desc-denoiseSimple_report.html"
        == generated_target
    )

    source_file = "sub-01_ses-ah_task-rest_run-1_space-MNIfake_res-2_desc-brain_mask.nii.gz"

    generated_target = utils.output_filename(
        source_file=source_file,
        atlas=atlas,
        suffix="dseg",
        extension="nii.gz",
        strategy="",
        atlas_desc=atlas_desc,
    )
    assert "sub-01_seg-fake100_dseg.nii.gz" == generated_target

    generated_target = utils.output_filename(
        source_file=source_file,
        atlas="",
        suffix="mask",
        extension="nii.gz",
        strategy="",
        atlas_desc="",
    )
    assert (
        "sub-01_space-MNIfake_res-2_label-GM_mask.nii.gz" == generated_target
    )
