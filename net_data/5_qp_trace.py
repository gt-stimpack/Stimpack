
import pandas as pd
import subprocess
import re
import os
import glob

def get_average_qp(target_kbps, sample_video):
    temp_out = "nul" if os.name == 'nt' else "/dev/null"

    command = [
        'ffmpeg', '-y',
        '-i', sample_video,
        '-t', '1',
        '-c:v', 'libx264',
        '-b:v', f'{target_kbps}k', # bits/second default by ffmpeg
        '-maxrate', f'{target_kbps}k',
        '-bufsize', f'{target_kbps}k',
        '-tune', 'zerolatency',
        '-preset', 'ultrafast',
        '-f', 'mp4', temp_out
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        log = result.stderr
        pattern = r"Avg QP:\s*(\d+\.?\d*)"
        qps = re.findall(pattern, log)
        print(qps)
        qps = [float(qp) for qp in qps]
        # there are two matches, print both
        if qps:
            qp_avg = sum(qps) / len(qps)
            return int(qp_avg)
    except Exception as e:
        print(f"\n[Error] {e}")
    return None


def add_qp_trace(input_dir, data_dir, reference_video):
    csv_dir = os.path.join(input_dir, data_dir)
    output_dir = os.path.join(input_dir, 'csv_with_qp')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    csv_files = glob.glob(os.path.join(csv_dir, '*.csv'))
    FINAL_COLUMN_NAMES = ['ts', 'bytes', 'elapsed_ms', 'kbps', 'qp']
    for csv_file in csv_files:
        try:
            fn = os.path.basename(csv_file)
            df = pd.read_csv(csv_file, header=0)
            if 'kbps' not in df.columns or df.shape[1] != 4:
                print(f"[Skipping] {fn} - 'kbps' column missing or incorrect number of columns.")
                continue

            if not os.path.exists(reference_video):
                print(f"No File Error: {reference_video}")
                return

            unique_kbps = df['kbps'].unique()
            kbps_to_qp_map = {}
            for i, kbps in enumerate(unique_kbps):
                qp = get_average_qp(kbps, reference_video)
                print(f"[{i+1}/{len(unique_kbps)}] {fn} Processing {kbps} kbps... --> QP: {qp}")
                kbps_to_qp_map[kbps] = qp

            df['qp'] = df['kbps'].map(kbps_to_qp_map)
            final_df = df[FINAL_COLUMN_NAMES].copy()
            final_df.columns = FINAL_COLUMN_NAMES

            output_path = os.path.join(output_dir, fn)
            final_df.to_csv(output_path, index=False)

        except Exception as e:
            print(f"[Error] {fn} - {e}")


if __name__ == "__main__":
    reference_video = os.path.expanduser('~/Videos/rev_60_.mp4')
    print(f"Reference video path: {reference_video}")
    if not os.path.exists(reference_video):
        print(f"No File Error: {reference_video}")
        exit()

    # dir_lists = ['3g/t1', '3g/t2', '3g/t3', '3g/t4', '3g/t5', '3g/t6', '3g/t7', '3g/t8', '3g/t9', '3g/t10', '3g/t11', '4g']
    # dir_lists = ['3g/t1', '3g/t2', '3g/t3', '3g/t4', '3g/t5', '3g/t6', '3g/t7', '3g/t8', '3g/t9', '3g/t10', '3g/t11']
    # dir_lists = ['3g/t1']
    # for dir_name in dir_lists:
    #     add_qp_trace(dir_name, 'csv_refined_mvavg', reference_video)

    dir_lists = ['4g']
    for dir_name in dir_lists:
        add_qp_trace(dir_name, 'csv_refined_mvavg', reference_video)
