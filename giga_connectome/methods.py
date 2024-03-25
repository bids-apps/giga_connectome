"""Module responsible for generating method section."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from nilearn import __version__ as nilearn_version
from templateflow import __version__ as templateflow_version

from giga_connectome import __version__


def generate_method_section(
    output_dir: Path,
    atlas: str,
    smoothing_fwhm: float,
    strategy: str,
    standardize: str,
    mni_space: str,
    average_correlation: bool,
) -> None:
    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent),
        autoescape=select_autoescape(),
        lstrip_blocks=True,
        trim_blocks=True,
    )

    template = env.get_template("data/methods/template.jinja")

    output_file = output_dir / "logs" / "CITATION.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    data = {
        "version": __version__,
        "nilearn_version": nilearn_version,
        "templateflow_version": templateflow_version,
        "atlas": atlas,
        "smoothing_fwhm": smoothing_fwhm,
        "strategy": strategy,
        "standardize": (
            "percent signal change" if standardize == "psc" else standardize
        ),
        "mni_space": mni_space,
        "average_correlation": average_correlation,
    }

    with open(output_file, "w") as f:
        print(template.render(data=data), file=f)
