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

In the following section, we will use this customised denoising strategy (5 aCompCor components, 6 motion parameters, global signal).
Run the following section in bash to create the denoising configuration file.

```bash
mkdir ${HOME}/customised_denoise
DENOISE_CONFIG=${HOME}/customised_denoise/denoise_config.json

# create denoise file
cat << EOF > ${DENOISE_CONFIG}
{
    "name": "custom_compcor",
    "function": "load_confounds",
    "parameters": {
        "strategy": ["high_pass", "motion", "compcor"],
        "motion": "basic",
        "n_compcor": 5,
        "compcor": "anat_combined",
        "global_signal": "basic",
        "demean": true
    }
}
EOF
```

2. Mount the path to the configuration file to the container and pass the **mounted path** to `--denoise-strategy`.

An example using Apptainer, with data downloaded as described in the [previous section](#download-the-example-dataset) :

```bash
# create denoising strategy
mkdir ${HOME}/customised_denoise/outputs
DATA=${HOME}/giga_connectome/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface
OUTPUT_DIR=${HOME}/customised_denoise/outputs
ATLASES_DIR=${HOME}/customised_denoise/outputs/atlas
DENOISE_CONFIG=${HOME}/customised_denoise/denoise_config.json

GIGA_CONNECTOME=${HOME}/giga-connectome.simg  # assuming the container is created in $HOME

apptainer run \
    --bind ${DATA}:/data/input \
    --bind ${OUTPUT_DIR}:/data/output \
    --bind ${ATLASES_DIR}:/data/atlases \
    --bind ${DENOISE_CONFIG}:/data/denoise_config.json \
    ${GIGA_CONNECTOME} \
    -a /data/atlases \
    --atlas Schaefer2018 \
    --denoise-strategy /data/denoise_config.json \
    --reindex-bids \
    /data/input \
    /data/output \
    participant
```

For Docker:

```bash
# create denoising strategy
mkdir ${HOME}/customised_denoise/outputs
DATA=${HOME}/giga_connectome/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface
OUTPUT_DIR=${HOME}/customised_denoise/outputs
ATLASES_DIR=${HOME}/customised_denoise/outputs/atlas
DENOISE_CONFIG=${HOME}/customised_denoise/denoise_config.json

docker run --rm \
    -v ${DATA}:/data/input \
    -v ${OUTPUT_DIR}:/data/output \
    -v ${ATLASES_DIR}:/data/atlases \
    -v ${DENOISE_CONFIG}:/data/denoise_config.json \
    bids/giga_connectome:unstable \
    /data/input \
    /data/output \
    participant \
    -a /data/atlases \
    --reindex-bids \
    --atlas Schaefer2018 \
    --denoise-strategy /data/denoise_config.json
```

### Atlas

1. Organise the atlas according to the [TemplateFlow](https://www.templateflow.org/python-client/0.7.1/naming.html) convention.

:::{warning}
`giga-connectome` and its upstream project `nilearn` did not explicitly test on non-standard templates, such as templates compiled from specific datasets or individual templates.
:::

A minimal set up should look like this:

```
/path/to/my_atlas/
  └──tpl-CustomisedTemplate/  # template directory of a valid template name
      ├── tpl-CustomisedTemplate_res-02_atlas-coolatlas_desc-256dimensions_probseg.nii.gz
      ├── tpl-CustomisedTemplate_res-02_atlas-coolatlas_desc-512dimensions_probseg.nii.gz
      └── tpl-CustomisedTemplate_res-02_atlas-coolatlas_desc-64dimensions_probseg.nii.gz
```

2. Update your TemplateFlow directory with network connection.

We will store our customised atlas under `${HOME}/customised_atlas/templateflow`.
This is an extremely important step in order to run the BIDS-app correctly without network connection.

```bash
mkdir -p ${HOME}/customised_atlas/templateflow
python3 -c "import os; from pathlib import Path; os.environ['TEMPLATEFLOW_HOME'] = f'{Path.home()}/customised_atlas/templateflow'; from templateflow.api import get; get(['MNI152NLin2009cAsym', 'MNI152NLin6Asym'])"
```

If your `CustomisedTemplate` is an existing TemplateFlow template, it should be added to the above line for download.
For example, you have a template in `MNI152NLin2009aAsym`:

```bash
mkdir -p ${HOME}/customised_atlas/templateflow
python3 -c "import os; from pathlib import Path; os.environ['TEMPLATEFLOW_HOME'] = f'{Path.home()}/customised_atlas/templateflow'; from templateflow.api import get; get(['MNI152NLin2009cAsym', 'MNI152NLin6Asym', 'MNI152NLin2009aAsym'])"
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

In the following section, we will generate an atlas on the test data using `nilearn.regions.Parcellations` with ward clustering method.
Run the following python code to generate the atlas and save to `${HOME}/customised_atlas/templateflow` in templateflow convention.

```python
from pathlib import Path
from nilearn.regions import Parcellations
from nilearn.datasets import load_mni152_gm_mask

data_paths = f"{Path.home()}/giga_connectome/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface/sub-*/ses-*/func/*space-MNI152NLin2009cAsym_res-2_desc-preproc_bold.nii.gz"
gm = load_mni152_gm_mask(resolution=4, threshold=0.5)
ward = Parcellations(
    method="ward",
    n_parcels=50,
    mask=gm,
    smoothing_fwhm=8.0,  # the example dataset is heavily downsampled
    standardize=False,
    memory="nilearn_cache",
    memory_level=1,
    verbose=1
)
ward.fit(data_paths)  # nilearn can comprehend wild card
ward_labels_img = ward.labels_img_

# Now, ward_labels_img are Nifti1Image object, it can be saved to file
# with the following code:

tpl_dir = Path.home() / "customised_atlas" / "templateflow" / "tpl-MNI152NLin2009cAsym"
tpl_dir.mkdir(exist_ok=True, parents=True)
print(f"Output will be saved to: {tpl_dir}")
ward_labels_img.to_filename(tpl_dir / "tpl-MNI152NLin2009cAsym_res-02_atlas-wardclustering_desc-50_dseg.nii.gz")
```

Create the configuration file:

```bash
ATLAS_CONFIG=${HOME}/customised_atlas/ward_config.json

# create denoise file
cat << EOF > ${ATLAS_CONFIG}
{
    "name": "wardclustering",
    "parameters": {
        "atlas": "wardclustering",
        "template": "MNI152NLin2009cAsym",
        "resolution": "02",
        "suffix": "dseg"
    },
    "desc": ["50"],
    "templateflow_dir": "/data/atlas"
}
EOF
```

4. Mount the path to the configuration file to the container and pass the **mounted path** to `--atlas`.
The path in your configuration file under `templateflow_dir` should be exported as an environment variable of the container.

An example using Apptainer:

```bash
mkdir ${HOME}/customised_atlas/outputs
DATA=${HOME}/giga_connectome/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface
OUTPUT_DIR=${HOME}/customised_atlas/outputs
OUTPUT_ATLASES_DIR=${HOME}/customised_atlas/outputs/atlas
ATLASES_DIR=${HOME}/customised_atlas/templateflow
ATLAS_CONFIG=${HOME}/customised_atlas/ward_config.json

GIGA_CONNECTOME=${HOME}/giga-connectome.simg  # assuming the container is created in $HOME

export APPTAINERENV_TEMPLATEFLOW_HOME=/data/atlas

apptainer run \
    --bind ${FMRIPREP_DIR}:/data/input \
    --bind ${OUTPUT_DIR}:/data/output \
    --bind ${ATLASES_DIR}:/data/atlas \
    --bind ${ATLAS_CONFIG}:/data/atlas_config.json \
    ${GIGA_CONNECTOME} \
    -a /data/atlas \
    --atlas /data/atlas_config.json \
    --denoise-strategy simple \
    /data/input \
    /data/output \
    participant
```

For Docker:

```bash
mkdir ${HOME}/customised_atlas/outputs
DATA=${HOME}/giga_connectome/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface
OUTPUT_DIR=${HOME}/customised_atlas/outputs
OUTPUT_ATLASES_DIR=${HOME}/customised_atlas/outputs/atlas
TFL_DIR=${HOME}/customised_atlas/templateflow
ATLAS_CONFIG=${HOME}/customised_atlas/ward_config.json

docker run --rm \
    -e TEMPLATEFLOW_HOME=/data/atlas \
    -v ${TFL_DIR}:/data/atlas \
    -v ${DATA}:/data/input \
    -v ${OUTPUT_DIR}:/data/output \
    -v ${OUTPUT_ATLASES_DIR}:/data/output/atlas \
    -v ${ATLAS_CONFIG}:/data/atlas_config.json \
    bids/giga_connectome:unstable \
    /data/input \
    /data/output \
    participant \
    -a /data/output/atlas \
    --atlas /data/atlas_config.json \
    --denoise-strategy simple
```
