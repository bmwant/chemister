import argparse

import pandas as pd

from download_rates import DATE_FMT


def main(filename, output_filename=None):
    output_filename = output_filename or filename
    df = pd.read_csv(filename)
    df.drop_duplicates(subset=['date'], inplace=True)
    df['date'] = pd.to_datetime(df['date'], format=DATE_FMT)
    df.sort_values(by=['date'], inplace=True)
    df.reset_index(drop=True, inplace=True)
    print(df.head())
    print(df.tail())
    print(df.describe())
    print('\nSaving into', output_filename)
    df.to_csv(
        output_filename,
        float_format='%.6f',
        date_format=DATE_FMT,
        index=False,
    )


def parse_args():
    parser = argparse.ArgumentParser(description='Preprocess data into uniform format.')
    parser.add_argument(
        'filename',
        type=str,
        help='which file you want to normalize',
    )
    parser.add_argument(
        '--output',
        required=False,
        type=str,
        help='where to save the result',
    )
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_args()
    main(filename=args.filename, output_filename=args.output)
