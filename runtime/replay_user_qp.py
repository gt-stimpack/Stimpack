import pandas as pd
import time
import subprocess
import sys
import os
import argparse
from runtime.common import rq_adjustment_period

report_script = "update_user_qp.py"

def main():
    parser = argparse.ArgumentParser(description="per-user QP replay")
    parser.add_argument("user_id", help="User ID in Stim")
    parser.add_argument("csv_file", help="Path to the input net trace file - csv format with qp column")

    args = parser.parse_args()
    user_id = args.user_id
    csv_path = args.csv_file
    print(f"User ID: {user_id}")
    print(f"CSV Path: {csv_path}")

    current_dir = os.path.dirname(os.path.abspath(__file__))
    report_script_path = os.path.join(current_dir, report_script)

    if not os.path.exists(csv_path):
        print(f"Error: '{csv_path}' Not Found...")
        return

    try:
        df = pd.read_csv(csv_path)
        if "qp" not in df.columns:
            print("Error: No 'qp' column in csv.")
            return
        qps = df["qp"].tolist()
    except Exception as e:
        print(f"Error: {e}")
        return

    print(f"{len(qps)} rows")

    try:
        while True:
            for i in range(0, len(qps), rq_adjustment_period):
                chunk = qps[i : i + rq_adjustment_period]

                if len(chunk) < rq_adjustment_period:
                    print("\nStart from beginning...")
                    break

                avg_value = int(sum(chunk) / len(chunk))
                print(f"Interval [{i}~{i+4}]: {avg_value}")

                try:
                    subprocess.run([sys.executable, report_script_path, str(user_id), str(avg_value)], check=True)
                except subprocess.CalledProcessError:
                    print(f"Error: {report_script} execution failed.")
                except FileNotFoundError:
                    print(f"Error: '{report_script_path}' Not Found.")
                    return

                time.sleep(rq_adjustment_period)

    except KeyboardInterrupt:
        print("\nExit...")


if __name__ == "__main__":
    main()

