# Outputs

When performing `participant` level analysis, the output is a HDF5 file per participant that was passed to `--participant_label` or all subjects under `bids_dir`.
The output file name is: `sub-<participant_id>_atlas-<atlas_name>_desc-<denoising_strategy>.h5`

When performing `group` level analysis, the file will contain time series and connectomes of each subject, as well as group average connectomes. The output is a HDF5 file per participant that was passed to `--participant_label` or all subjects under `bids_dir`.
The output file name is: `atlas-<atlas_name>_desc-<denoising_strategy>.h5`
