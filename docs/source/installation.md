# Installation

## Quick start (Docker)

Clone the project and build from `Dockerfile` (Recommended)

```
git clone git@github.com:SIMEXP/giga_connectome.git
cd giga_connectome
docker build . --file Dockerfile
docker run -ti --rm --read-only giga_connectome --help
```

Build from `Dockerfile` (Recommended):
```
docker build . --file Dockerfile
```

Install the project in a Python environment:
```
pip install .
```

For development:
```
pip install -e .[dev]
```
