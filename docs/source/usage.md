# Usage Notes

## Command line interface

```{eval-rst}
.. argparse::
   :prog: giga_connectome
   :module: giga_connectome.run
   :func: global_parser
```

## General usage

Here is an example of using the preset denoise strategies and atlases.

### Download the example dataset

We created a downsampled version of Open Neuro dataset
[ds000017](https://openneuro.org/datasets/ds000017/versions/00001)
hosted on [Zenodo page](https://zenodo.org/records/8091903).
You can download this dataset to understand how to use different options of `giga_connectome`.

You can download the data to any preferred location.
For the purpose of this tutorial, we will save the downloaded dataset under `giga_connectome/test_data`
in your home directory (`~/giga_connectome/test_data`).

Here is the download instruction for Linux/Mac users:

```bash
mkdir -p ~/giga_connectome/test_data
wget --retry-connrefused \
    --waitretry=5 \
    --read-timeout=20 \
    --timeout=15 \
    -t 0 \
    -q \
    -O ~/giga_connectome/test_data/ds000017.tar.gz \
    "https://zenodo.org/record/8091903/files/ds000017-fmriprep22.0.1-downsampled-nosurface.tar.gz?download=1"
tar -xzf ~/giga_connectome/test_data/ds000017.tar.gz -C ~/giga_connectome/test_data/
rm ~/giga_connectome/test_data/ds000017.tar.gz
```

Alternatively, you can go to the [Zenodo page](https://zenodo.org/records/8091903) and download
`ds000017-fmriprep22.0.1-downsampled-nosurface.tar.gz` and uncompress it.

Now you will find the dataset at `~/giga_connectome/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface`.
Under this directory, you will find a full fMRIPrep output layout of two subjects.

### Running `giga_connectome` with container

Given that you have already [installed the container](./installation.md), you can run `giga_connectome` with
[apptainer](https://apptainer.org/) as follow:

```bash
DATA=~/giga_connectome/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface
mkdir -p outputs/

apptainer run \
    --bind ${DATA}:/inputs \
    --bind ./outputs:/outputs \
    --bind ./outputs/atlases:/atlases \
    giga_connectome \
    /inputs \
    /outputs \
    participant \
    -a /atlases \
    --atlas Schaefer2018 \
    --denoise-strategy simple \
    --reindex-bids
```

For Docker:

```bash
DATA=${HOME}/giga_connectome/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface
mkdir -p outputs/

docker run --rm \
    -v ${DATA}:/test_data \
    -v ./outputs:/outputs \
    -v ./outputs/atlases:/atlases \
    bids/giga_connectome \
    /test_data \
    /outputs \
    participant \
    -a /atlases \
    --atlas Schaefer2018 \
    --denoise-strategy simple \
    --reindex-bids
```

Now you can navigate the outputs under `outputs`

## Advanced: Using customised configuration files for denoising strategy and atlas

Aside from the preset strategies and atlases, the users can supply their own for further customisation.
We encourage the users to use the container version of the BIDS app, hence all documentation below will relect on the usage of the container.
Users can use the preset template as examples for creating their own configuration files.
This section will walk through the details of the configuration files and extra steps needed.

All presets can be found in [`giga_connectome/data`](https://github.com/bids-apps/giga_connectome/tree/main/giga_connectome/data).

### Denoising strategy

1. Create the configuration file.

The tool uses `nilearn.interfaces.fmriprep.load_confounds` and `nilearn.interfaces.fmriprep.load_confounds_strategy`
as the way of retrieving confounds.

In a `json` file, define the customised strategy in the following format:

```
{
    "name": "<name_of_the_strategy>",
    "function": "<load_confounds>, <load_confounds_strategy>",
    "parameters": {
        "<function_parameters>": "<options>",
        ....
    }
}
```

See examples in [`giga_connectome/data/denoise_strategy`](https://github.com/bids-apps/giga_connectome/tree/main/giga_connectome/data/denoise_strategy).

2. Mount the path to the configuration file to the container and pass the **mounted path** to `--denoise-strategy`.

An example using Apptainer (formerly known as Singularity):

```bash
FMRIPREP_DIR=/path/to/fmriprep_output
OUTPUT_DIR=/path/to/connectom_output
ATLASES_DIR=/path/to/atlases
DENOISE_CONFIG=/path/to/denoise_config.json

GIGA_CONNECTOME=/path/to/giga-connectome.simg

apptainer run \
    --bind ${FMRIPREP_DIR}:/data/input \
    --bind ${OUTPUT_DIR}:/data/output \
    --bind ${ATLASES_DIR}:/data/atlases \
    --bind ${DENOISE_CONFIG}:/data/denoise_config.json \
    ${GIGA_CONNECTOME} \
    -a /data/atlases \
    --denoise-strategy /data/denoise_config.json \
    /data/input \
    /data/output \
    participant
```

### Atlas

1. Organise the atlas according to the [TemplateFlow](https://www.templateflow.org/python-client/0.7.1/naming.html) convention.

A minimal set up should look like this:

```
/path/to/my_atlas/
  └──tpl-CustomisedTemplate/  # template directory of a valid template name
      ├── tpl-CustomisedTemplate_res-02_atlas-coolatlas_desc-256dimensions_probseg.nii.gz
      ├── tpl-CustomisedTemplate_res-02_atlas-coolatlas_desc-512dimensions_probseg.nii.gz
      └── tpl-CustomisedTemplate_res-02_atlas-coolatlas_desc-64dimensions_probseg.nii.gz
```

2. Update your TemplateFlow directory with network connection.

This is an extremely important step in order to run the BIDS-app correctly without network connection.

```bash
python3 -c "import os; from templateflow.api import get; os.environ['TEMPLATEFLOW_HOME'] = '/path/to/my_atlas'; get(['MNI152NLin2009cAsym', 'MNI152NLin6Asym'])"
```

If your `CustomisedTemplate` is an existing TemplateFlow template, it should be added to the above line for download.
For example, you have a template in `MNI152NLin2009aAsym`:

```bash
python3 -c "import os; from templateflow.api import get; os.environ['TEMPLATEFLOW_HOME'] = '/path/to/my_atlas'; get(['MNI152NLin2009cAsym', 'MNI152NLin6Asym', 'MNI152NLin2009aAsym'])"
```

3. Create your config file.

In a `json` file, define the customised atlas. We will use the atlas above as an example.
It's very important to specify `templateflow_dir` otherwise the BIDS-app will search for the default already downloaded in the container.
`templateflow_dir` should be the target you will be mounting to the BIDS-app container, rather than the location on your disc.

Example:
```
{
    "name": "<name_of_atlas>",  # for simplicity, one can use the 'atlas' field of the file name
    "parameters": {  # the fields in this section should all be present and consistent with your atlas, except 'desc'
        "atlas": "coolatlas",  # this should match the 'atlas' field of the file name
        "template": "CustomisedTemplate",
        "resolution": "02",
        "suffix": "probseg"
    },
    "desc": [  # entity desc of the atlases
        "64dimensions",
        "128dimensions",
        "256dimensions"],
    "templateflow_dir" : "/data/atlas"  # the target path you will be mounting to the BIDS-app container
}
```

See examples in [`giga_connectome/data/atlas/`](https://github.com/bids-apps/giga_connectome/tree/main/giga_connectome/data/atlas).

4. Mount the path to the configuration file to the container and pass the **mounted path** to `--atlas`.
The path in your configuration file under `templateflow_dir` should be exported as an environment variable of the container.

An example using Apptainer (formerly known as Singularity):

```bash
FMRIPREP_DIR=/path/to/fmriprep_output
OUTPUT_DIR=/path/to/connectom_output
ATLASES_DIR=/path/to/atlases
ATLAS_CONFIG=/path/to/atlas_config.json

GIGA_CONNECTOME=/path/to/giga-connectome.simg

export APPTAINERENV_TEMPLATEFLOW_HOME=/data/atlas

apptainer run \
    --bind ${FMRIPREP_DIR}:/data/input \
    --bind ${OUTPUT_DIR}:/data/output \
    --bind ${ATLASES_DIR}:/data/atlases \
    --bind ${ATLAS_CONFIG}:/data/atlas_config.json \
    ${GIGA_CONNECTOME} \
    -a /data/atlases \
    --atlas /data/atlas_config.json \
    /data/input \
    /data/output \
    participant
```
