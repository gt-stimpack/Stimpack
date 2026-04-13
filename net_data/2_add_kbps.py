import pandas as pd
import numpy as np
import os
import glob

MAG_FACTOR = 8


def refine_csv_file(input_dir):
    output_dir = os.path.join(input_dir, 'csv_refined')



def transform_all_csv_files(input_directory=".", output_directory="refined"):
    # Create the output directory if it does not exist
    output_path = os.path.join(input_directory, output_directory)
    os.makedirs(output_path, exist_ok=True)

    # Use glob to find all CSV files in the input directory
    search_path = os.path.join(input_directory, "*.csv")
    csv_files = glob.glob(search_path)

    if not csv_files:
        print("INFO: No CSV files found in the directory.")
        return

    print(f"INFO: Found {len(csv_files)} CSV files to process.")

    processed_count = 0

    # Define the target column names
    FINAL_COLUMN_NAMES = ['ts', 'bytes', 'elapsed_time', 'kbps']

    for input_filepath in csv_files:
        try:
            filename = os.path.basename(input_filepath)
            print(f"PROCESSING: Starting transformation for {filename}")

            # 1. Read the CSV file (assuming no header)
            df = pd.read_csv(input_filepath, header=True)

            # Check for the minimum required number of columns (6)
            if df.shape[1] < 6:
                print(f"WARNING: File {filename} has less than 6 columns. Skipping.")
                continue

            # Temporarily assign names corresponding to the index
            df.columns = [f'Col{i}' for i in range(6)]

            # --- 1. Transform Col0 (ts): Difference from previous row ---
            # Original Col0 is the input for the new 'ts' column
            df['New_ts'] = (df['Col0'] - df['Col0'].shift(1)).fillna(0)

            # --- 2. Create New Last Column (kbs): Col4 / Col5 ---
            # Handle division by zero: if Col5 is 0, set the result to 0.
            # Original Col4 is the new 'bytes' column.
            # Original Col5 is the new 'elapsed_time' column.
            df['New_kbps'] = np.where(
                df['Col5'] != 0,
                df['Col4'] / df['Col5'] * 8,
                0
            )

            # --- 3. Select final 4 columns and reorder ---
            # The columns to be retained are:
            # - New_ts (Transformed Col 0)
            # - Original Col4 (The new 'bytes' column)
            # - Original Col5 (The new 'elapsed_time' column)
            # - New_kbps (The calculated ratio)

            final_df = df[['New_ts', 'Col4', 'Col5', 'New_kbps']].copy()

            # Assign the requested final column names
            final_df.columns = FINAL_COLUMN_NAMES

            # --- 4. Save to the 'refined' subfolder ---
            output_filepath = os.path.join(output_path, filename)
            final_df.to_csv(output_filepath, index=False)

            print(f"SUCCESS: Saved transformed data to {output_filepath}")
            processed_count += 1

        except Exception as e:
            print(f"ERROR: Failed to process file {filename}. Error: {e}")

    print("-" * 50)
    print(f"SUMMARY: Total files processed: {processed_count} out of {len(csv_files)}")
    print(f"Output directory: {output_path}")

if __name__ == "__main__":
    dir_lists = ['t1', 't2', 't3', 't4', 't5', 't6', 't7', 't8', 't9', 't10', 't11']
    for dir_name in dir_lists:
        transform_all_csv_files()

