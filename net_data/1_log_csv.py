import os
import csv

def convert_logs_to_csv(input_dir="."):
    output_dir = os.path.join(input_dir, 'csv')
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        return

    for filename in os.listdir(input_dir):
        if filename.endswith(".log") and filename != 'csv':
            input_filepath = os.path.join(input_dir, filename)

            base_filename = filename[:-4]  # remove '.log'
            output_filename = f"{base_filename}.csv"
            output_filepath = os.path.join(output_dir, output_filename)

            print(f"\nconverting: {filename}")

            try:
                with open(input_filepath, 'r', encoding='utf-8') as infile:
                    with open(output_filepath, 'w', newline='', encoding='utf-8') as outfile:
                        # if output file exists, it will be overwritten
                        csv_writer = csv.writer(outfile)
                        for line in infile:
                            data = line.strip().split()
                            if data:
                                csv_writer.writerow(data)
            except FileNotFoundError:
                print(f"Cannot find dir: {input_filepath}")
            except Exception as e:
                print(f"Processing error: {e}")

if __name__ == "__main__":
    dir_lists = ['3g/t1', '3g/t2', '3g/t3', '3g/t4', '3g/t5', '3g/t6', '3g/t7', '3g/t8', '3g/t9', '3g/t10', '3g/t11', '4g']
    for dir_name in dir_lists:
        convert_logs_to_csv(input_dir = dir_name)

