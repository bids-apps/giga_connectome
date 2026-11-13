import pytest

from giga_connectome.atlas import get_atlas_labels, load_atlas_setting
from giga_connectome.data import DATA_DIR


def test_load_atlas_setting() -> None:
    atlas_config = load_atlas_setting("Schaefer2018")
    assert atlas_config["name"] == "Schaefer2018"
    atlas_config = load_atlas_setting("HarvardOxfordCortical")
    assert atlas_config["name"] == "HarvardOxfordCortical"
    with pytest.raises(FileNotFoundError):
        load_atlas_setting("blah")
    json_path = DATA_DIR / "atlas" / "DiFuMo.json"
    atlas_config = load_atlas_setting(json_path)
    assert atlas_config["name"] == "DiFuMo"


def test_get_atlas_labels_sorted() -> None:
    """The labels end up in the CLI help and descriptor.json, so their order
    must not depend on the file system.
    """
    labels = get_atlas_labels()
    assert labels == sorted(labels)
    assert "Schaefer2018" in labels
