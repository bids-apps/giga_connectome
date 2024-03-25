# Usage Notes

## Command line interface

```{eval-rst}
.. argparse::
   :prog: giga_connectome
   :module: giga_connectome.run
   :func: global_parser
```

## Writing configuration files

All preset can be found in [`giga_connectome/data`](https://github.com/SIMEXP/giga_connectome/tree/main/giga_connectome/data).

### Denoising strategy

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

See examples in [`giga_connectome/data/denoise_strategy`](https://github.com/SIMEXP/giga_connectome/tree/main/giga_connectome/data/denoise_strategy).

### Atlas

After the atlas files are organised according to the [TemplateFlow](https://www.templateflow.org/python-client/0.7.1/naming.html) convention.

A minimal set up should look like this:

```
my_atlas/
  └──tpl-MNI152NLin2009cAsym/  # template directory of a valid template name
      ├── tpl-MNI152NLin2009cAsym_res-02_atlas-coolatlas_desc-256dimensions_probseg.nii.gz
      ├── tpl-MNI152NLin2009cAsym_res-02_atlas-coolatlas_desc-512dimensions_probseg.nii.gz
      └── tpl-MNI152NLin2009cAsym_res-02_atlas-coolatlas_desc-64dimensions_probseg.nii.gz
```

In a `json` file, define the customised atlas. We will use the atlas above as an example:

```
{
    "name": "<name_of_atlas>",
    "parameters": {  # the fields in this section should all be present and consistent with your atlas, except 'desc'
        "atlas": "coolatlas",
        "template": "MNI152NLin2009cAsym",
        "resolution": "02",
        "suffix": "probseg"
    },
    "desc": [  # entity desc of the atlases
        "64dimensions",
        "128dimensions",
        "256dimensions"],
    "templateflow_dir" : "my_atlas/"  # To use the default templateflow directory, set value to null
}
```

See examples in [`giga_connectome/data`](https://github.com/SIMEXP/giga_connectome/tree/main/giga_connectome/data).


## Example

You can run a demo of the bids app by downloading some test data.

Run the following from the root of the repository.

```bash
pip install tox
tox -e test_data
```

```bash
giga_connectome \
    --atlas Schaefer20187Networks \
    --denoise-strategy simple \
    --standardize zscore \
    --bids-filter giga_connectome/data/test_data/bids_filter.json  \
    --reindex-bids \
    --calculate-intranetwork-average-correlation \
    giga_connectome/data/test_data/ds000017-fmriprep22.0.1-downsampled-nosurface \
    giga_connectome/data/test_data/output \
    participant
```
