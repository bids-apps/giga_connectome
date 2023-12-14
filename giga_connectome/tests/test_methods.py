from giga_connectome import methods


def test_generate_method_section(tmp_path):
    methods.generate_method_section(output_dir=tmp_path)
