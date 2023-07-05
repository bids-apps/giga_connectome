from pathlib import Path
from bids.tests import get_test_data_path
from giga_connectome import utils


def test_parse_bids_name():
    subject, session, specifier = utils.parse_bids_name(
        "sub-01_ses-ah_task-rest_run-1_space-MNIfake_res-2_desc-preproc_bold.nii.gz"
    )
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
