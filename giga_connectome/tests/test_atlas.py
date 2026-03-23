import pytest

from giga_connectome.atlas import load_atlas_setting
from giga_connectome.data import DATA_DIR


def test_load_atlas_setting():
    # use Schaefer2018 when updating 0.7.0
    atlas_config = load_atlas_setting("Schaefer20187Networks")
    assert atlas_config["name"] == "Schaefer2018"
    atlas_config = load_atlas_setting("Schaefer2018")
    assert atlas_config["name"] == "Schaefer2018"
    atlas_config = load_atlas_setting("HarvardOxfordCortical")
    assert atlas_config["name"] == "HarvardOxfordCortical"
    with pytest.raises(FileNotFoundError):
        load_atlas_setting("blah")
    json_path = DATA_DIR / "atlas" / "DiFuMo.json"
    atlas_config = load_atlas_setting(json_path)
    assert atlas_config["name"] == "DiFuMo"
