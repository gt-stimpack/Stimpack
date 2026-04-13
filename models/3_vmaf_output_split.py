import csv
import os

def generate_train_test_sets(input_file, target_cam_list):
    try:
        with open(input_file, 'r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            source_data = list(reader) # all rows from input CSV as list of dicts
    except FileNotFoundError:
        print(f"'{input_file}' Not Found.")
        return

    new_fieldnames = ['codec', 'rq', 'qp', 'vmaf']

    for cam_id in target_cam_list:
        target_cam_str = str(cam_id)

        output_dir = f"./{target_cam_str}"
        os.makedirs(output_dir, exist_ok=True)

        test_path = os.path.join(output_dir, 'test.csv')
        train_path = os.path.join(output_dir, 'train.csv')

        print(f"Processing Cam {target_cam_str}...: {output_dir}")

        with open(test_path, 'w', newline='', encoding='utf-8') as f_test, \
             open(train_path, 'w', newline='', encoding='utf-8') as f_train:

            writer_test = csv.DictWriter(f_test, fieldnames=new_fieldnames)
            writer_train = csv.DictWriter(f_train, fieldnames=new_fieldnames)

            writer_test.writeheader()
            writer_train.writeheader()

            test_count = 0
            train_count = 0

            for row in source_data:
                new_row = {
                    'codec': 'h264',
                    'rq': row['rq'],
                    'qp': row['qp'],
                    'vmaf': row['vmaf']
                }

                if row['cam'] == target_cam_str:
                    writer_test.writerow(new_row)
                    test_count += 1
                else:
                    writer_train.writerow(new_row)
                    train_count += 1

            print(f"  - Done: Test({test_count}), Train({train_count})")


input_csv = 'output_cam.csv'
cam_list = [1, 2, 3, 4, 5]

generate_train_test_sets(input_csv, cam_list)

