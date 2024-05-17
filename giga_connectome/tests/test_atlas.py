from giga_connectome.atlas import load_atlas_setting


def test_load_atlas_setting():
    atlas_config = load_atlas_setting("Schaefer2018")
    assert atlas_config["name"] == "Schaefer2018"
    atlas_config = load_atlas_setting("HarvardOxfordCortical")
    assert atlas_config["name"] == "HarvardOxfordCortical"
