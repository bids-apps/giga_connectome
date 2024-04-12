# Installation

## Quick start (container)

Pull the latest image from docker hub, available for version > `0.5.0`(Recommended)

Apptainer (formerly known as Singularity; recommended):

```bash
apptainer build giga_connectome.simg docker://bids/giga_connectome:latest
```

Docker:
```bash
docker pull bids/giga_connectome:latest
```

## Install as a python package

Install the project in a Python environment:

```bash
pip install git+https://github.com/bids-apps/giga_connectome.git
```

This method is available for all versions.
Change the tag based on version you would like to use.
