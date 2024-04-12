from giga_connectome import load_atlas_setting


def test_load_atlas_setting():
    atlas_config = load_atlas_setting("Schaefer20187Networks")
    assert atlas_config["name"] == "Schaefer20187Networks"
    atlas_config = load_atlas_setting("HarvardOxfordCortical")
    assert atlas_config["name"] == "HarvardOxfordCortical"
