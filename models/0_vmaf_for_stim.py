import os
import subprocess
import re
import csv

# prerequisites:
# docker pull gfdavila/easyvmaf

def get_case(scene, rq, camera, qp):
    return scene + '_' + rq + '_' + camera + '_' + qp + '.mp4'

def get_ref_case(scene, rq, camera):
    return scene + '_' + rq + '_' + camera + '.mp4'

ref_rq = '3'
scenes = ['town', 'sky', 'desert', 'desk', 'forest']
rqs = ['3', '2', '1', '0']
cameras = ['c1', 'c2', 'c3', 'c4', 'c5']
qps = ['qp5', 'qp10', 'qp15', 'qp20', 'qp25', 'qp30', 'qp35', 'qp40', 'qp45', 'qp50']

vid_home = os.path.dirname(os.path.realpath(__file__)) + "/game_vid/"
ref_dir_name = "ref"
ref_dir = os.path.join(vid_home, ref_dir_name)
print(vid_home)
print(ref_dir)

csv_results = {}

# ref file example: town_3_c1.mp4
# comp file example: town_3_c1_qp5.mp4

for scene in scenes:
    for rq in rqs:
        comp_dir_name = scene + "_" + rq + "_clips"
        comp_dir = os.path.join(vid_home, comp_dir_name) # ./game_vid/town_0_clips/
        print(comp_dir)
        for camera in cameras:
            ref_case = get_ref_case(scene, ref_rq, camera) # town_3_c1.mp4
            ref_vid = os.path.join(ref_dir, ref_case)  # ./game_vid/ref/town_3_c1.mp4
            print(ref_vid)
            for qp in qps:
                case = get_case(scene, rq, camera, qp)  # town_3_c1_qp5.mp4
                comp_vid = os.path.join(comp_dir, case) # ./game_vid/town_0_clips/town_3_c1_qp5.mp4
                print("\t", comp_vid)
                command = f"docker run --rm -v {vid_home}:/game_vid gfdavila/easyvmaf -r /game_vid/ref/{ref_case} -d /game_vid/{comp_dir_name}/{case}"

                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                result = re.search(r'VMAF score \(arithmetic mean\):\s*([0-9.]+)', result.stdout)
                vmaf_score = float(result.group(1))
                csv_results[case] = vmaf_score
                print(f"VMAF score for {case}: {vmaf_score}")

# write to csv
csv_file = "vmaf_results.csv"
with open(csv_file, mode='w') as file:
    writer = csv.writer(file)
    writer.writerow(["case", "vmaf_score"])
    for case, score in csv_results.items():
        writer.writerow([case, score])

