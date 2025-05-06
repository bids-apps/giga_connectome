# Installation

## Quick start (container)

Pull the latest image from docker hub, available for version > `0.5.0`(Recommended)

Apptainer (recommended):

```bash
apptainer build giga_connectome.simg docker://bids/giga_connectome:latest
```

Docker:
```bash
docker pull bids/giga_connectome:latest
```

## Install as a python package (not recommended)

The project is written as an installable python package, however,
it is not recommended for non contributors.

If you wish to install giga-connectome as a python package,
please follow the full instruction in
[Setting up your environment for development](./contributing.md#setting-up-your-environment-for-development) step 1 to 4.
These steps will ensure the installed package retain all the functions as the container image.
