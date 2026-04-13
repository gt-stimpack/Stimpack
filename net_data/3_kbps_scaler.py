import pandas as pd
import numpy as np
import os
import glob

SCALE_FACTOR = 5

def scale_csv_file(input_dir):
    csv_dir = os.path.join(input_dir, 'csv_refined')
    output_dir = os.path.join(input_dir, 'csv_refined_scaled')
    os.makedirs(output_dir, exist_ok=True)

    csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))
    FINAL_COLUMN_NAMES = ['ts', 'bytes', 'elapsed_ms', 'kbps']

    for csv_file in csv_files:
        try:
            fn = os.path.basename(csv_file)
            print(f"PROCESSING: Starting transformation for {fn}")
            df = pd.read_csv(csv_file, header=0)
            # print(df.head())

            if df.shape[1] != 4:
                print(f"WARNING: File {fn} columns != 4. Skipping.")
                continue

            # df.columns = FINAL_COLUMN_NAMES
            df['kbps'] = df['kbps'] * SCALE_FACTOR
            df.loc[df['kbps'] > 15000, 'kbps'] *= 2.3
            df['kbps'] = df['kbps'].round().astype(int)

            final_df = df[['ts', 'bytes', 'elapsed_ms', 'kbps']].copy()
            final_df.columns = FINAL_COLUMN_NAMES

            output_path = os.path.join(output_dir, fn)
            final_df.to_csv(output_path, index=False)
            print(f"SUCCESS: Saved transformed data to {output_path}")

        except Exception as e:
            print(f"ERROR: Failed to process file {fn}. Error: {e}")


if __name__ == "__main__":
    dir_lists = ['3g/t1', '3g/t2', '3g/t3', '3g/t4', '3g/t5', '3g/t6', '3g/t7', '3g/t8', '3g/t9', '3g/t10', '3g/t11']
    for dir_name in dir_lists:
        scale_csv_file(input_dir = dir_name)

    scale_csv_file(input_dir = dir_name)
