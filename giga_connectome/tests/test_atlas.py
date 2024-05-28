from giga_connectome.atlas import load_atlas_setting
import pytest
from pkg_resources import resource_filename


def test_load_atlas_setting():
    # use Schaefer2018 when updating 0.7.0
    atlas_config = load_atlas_setting("Schaefer20187Networks")
    assert atlas_config["name"] == "Schaefer2018"
    atlas_config = load_atlas_setting("Schaefer2018")
    assert atlas_config["name"] == "Schaefer2018"
    atlas_config = load_atlas_setting("HarvardOxfordCortical")
    assert atlas_config["name"] == "HarvardOxfordCortical"
    pytest.raises(FileNotFoundError, load_atlas_setting, "blah")
    json_path = resource_filename("giga_connectome", "data/atlas/DiFuMo.json")
    atlas_config = load_atlas_setting(json_path)
    assert atlas_config["name"] == "DiFuMo"
