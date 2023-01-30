# """
# Process fMRIPrep outputs to timeseries based on denoising strategy.
# """
# import argparse
# from pathlib import Path

# from giga_connectome.fmriprep import (
#     get_prepro_strategy,
#     fetch_fmriprep_derivative,
# )
# from giga_connectome.timeseries import (
#     generate_timeseries_per_dimension,
# )


# def parse_args():
#     parser = argparse.ArgumentParser(
#         formatter_class=argparse.RawTextHelpFormatter,
#         description=(
#             'Generate connectome based on denoising strategy for '
#             'fmriprep processed dataset.'
#         ),
#     )
#     parser.add_argument(
#         'output_path',
#         action='store',
#         type=str,
#         help='output path for connectome.',
#     )
#     parser.add_argument(
#         '--fmriprep_path',
#         action='store',
#         type=str,
#         help='Path to a fmriprep detrivative.',
#     )
#     parser.add_argument(
#         '--dataset_name', action='store', type=str, help='Dataset name.'
#     )
#     parser.add_argument(
#         '--subject', action='store', type=str, help='subject id.'
#     )
#     parser.add_argument(
#         '--atlas',
#         action='store',
#         type=str,
#         help='Atlas name (schaefer7networks, MIST, difumo, gordon333)',
#     )
#     return parser.parse_args()


# def main():
#     args = parse_args()
#     print(vars(args))
#     dataset_name = args.dataset_name
#     subject = args.subject
#     strategy_name = None
#     atlas_name = args.atlas
#     derivative = Path(args.fmriprep_path)
#     output_root = Path(args.output_path)

#     ts_output = output_root / f'atlas-{atlas_name}'
#     ts_output.mkdir(exist_ok=True, parents=True)

#     benchmark_strategies = get_prepro_strategy(strategy_name)

#     generate_timeseries_per_dimension(
#         atlas_name, ts_output, benchmark_strategies, derivative, subject
#     )


# if __name__ == '__main__':
#     main()
