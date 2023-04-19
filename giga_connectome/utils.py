from typing import List
from nilearn.interfaces.bids import parse_bids_filename


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


def get_bids_basename(img: str, template: str) -> str:
    """fMRIprep file base name with template space."""
    subject, session, specifier = parse_bids_name(img)
    return f"{subject}_{session}_{specifier}_space-{template}"
