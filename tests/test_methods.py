from giga_connectome import methods


def test_generate_method_section(tmp_path):
    methods.generate_method_section(
        output_dir=tmp_path,
        atlas="DiFuMo",
        smoothing_fwhm=5,
        standardize="psc",
        strategy="simple",
        mni_space="MNI152NLin6Asym",
        average_correlation=True,
    )
