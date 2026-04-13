import csv
import re

def convert_vmaf_scores(input_file, output_file):
    # Read the input CSV file
    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)
        data = list(reader)

    # Prepare the output data
    output_data = []

    # Process each row in the input data
    for row in data:
        case = row['case']
        vmaf_score = row['vmaf_score']

        # Extract RQ and QP from the case name using regex
        match = re.match(r'.*?_(\d)_.*?_qp(\d+)\.mp4', case)
        if match:
            rq, qp = match.groups()

            # Construct the new row for the output CSV
            output_data.append(['h264', rq, qp, vmaf_score])

    # Write the output CSV file
    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(['codec', 'rq', 'qp', 'vmaf'])  # Write header
        writer.writerows(output_data)

# Example usage
input_file = './vmaf_results.csv'
output_file = 'output.csv'
convert_vmaf_scores(input_file, output_file)
