# Workflow

1. Create group level / subject specific grey matter mask in MNI space.

2. Sample the atlas to the space of group level  / subject specific grey matter mask in MNI space.

3. Calculate the conjunction of the customised grey matter mask and resampled atlas to find valid parcels.

4. Use the new input specific grey matter mask and atlas to extract time series and connectomes for each subject.

5. Calculate intranetwork correlation of each parcel. The values replace the diagonal of the connectomes.

6. Create a group average connectome (if analysis level is `group`).
