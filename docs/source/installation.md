# Installation

## Quick start (Docker)

Pull the latest image from docker hub, available for version > `0.4.0`(Recommended)

Singularity:

```bash
singularity build giga_connectome.simg docker://haotingwang/giga_connectome:latest
```

Docker:
```bash
docker pull haotingwang/giga_connectome:latest
```

## Install as a python package

Install the project in a Python environment:

```bash
pip install git+https://github.com/SIMEXP/giga_connectome.git@0.4.0
```

This method is available for all versions.
Change the tag based on version you would like to use.
