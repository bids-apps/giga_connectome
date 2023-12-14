"""Module responsible for generating method section."""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from giga_connectome import __version__


def generate_method_section(output_dir: Path):

    env = Environment(
        loader=FileSystemLoader(Path(__file__).parent),
        autoescape=select_autoescape(),
        lstrip_blocks=True,
        trim_blocks=True,
    )

    template = env.get_template("data/methods/template.jinja")

    output_file = output_dir / "logs" / "CITATION.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    data = {"version": __version__}

    with open(output_file, "w") as f:
        print(template.render(data=data), file=f)
