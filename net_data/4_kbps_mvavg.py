import pandas as pd
import os
import glob

WND_SIZE = 10

def mvavg_csv_file(input_dir, data_dir):
    csv_dir = os.path.join(input_dir, data_dir)
    output_dir = os.path.join(input_dir, 'csv_refined_mvavg')
    os.makedirs(output_dir, exist_ok=True)

    csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))
    FINAL_COLUMN_NAMES = ['ts', 'bytes', 'elapsed_ms', 'kbps']

    for csv_file in csv_files:
        try:
            fn = os.path.basename(csv_file)
            df = pd.read_csv(csv_file, header=0)
            if "kbps" not in df.columns:
                print(f"WARNING: 'kbps' column not found in {fn}. Skipping file.")
                continue
            df['kbps'] = df['kbps'].rolling(window=WND_SIZE, min_periods=1).mean()
            df['kbps'] = df['kbps'].round().astype(int)
            df.columns = FINAL_COLUMN_NAMES

            output_file = os.path.join(output_dir, fn)
            df.to_csv(output_file, index=False)
            print(f"SUCCESS: Processed and saved {fn} with moving average.")

        except Exception as e:
            print(f"ERROR: Failed to read {fn}. Error: {e}")
            continue


if __name__ == "__main__":
    dir_lists = ['3g/t1', '3g/t2', '3g/t3', '3g/t4', '3g/t5', '3g/t6', '3g/t7', '3g/t8', '3g/t9', '3g/t10', '3g/t11']
    data_dir = 'csv_refined_scaled'
    for dir_name in dir_lists:
        mvavg_csv_file(dir_name, data_dir)

    mvavg_csv_file('4g', 'csv_refined')
