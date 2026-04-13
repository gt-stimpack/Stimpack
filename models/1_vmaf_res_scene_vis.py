import csv
import re
import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
from collections import defaultdict

# === 설정 ===
INPUT_FILE = './vmaf_results.csv'
OUTPUT_DIR = './scene_summary'
# 정규표현식: [case name]_[lv]_[c#]_qp[qp].mp4 패턴 매칭
# 예: town_3_c1_qp5.mp4 -> group(1): town, group(2): 3, group(3): 1, group(4): 5
REGEX_PATTERN = r'^([a-zA-Z0-9_]+)_(\d)_c(\d)_qp(\d+)\.mp4$'

lv_labels = {0: 'Low', 1: 'Medium', 2: 'High', 3: 'Very High'}

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
plt.rc('font', size=20)


def process_and_aggregate_data(input_file):
    """
    result[case_name][lv][qp] = [vmaf list ...]
    """
    print(f"Processing data from: {input_file}...")
    # 3중 중첩 defaultdict 생성 (값을 리스트로 초기화)
    # result['town']['3']['5'] = [] 형태가 됨
    result_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    try:
        with open(input_file, 'r', encoding='utf-8-sig') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                case_filename = row['case']
                try:
                    vmaf_score = float(row['vmaf_score'])
                except ValueError:
                    print(f"Warning: Skipped invalid VMAF score in row: {row}")
                    continue

                match = re.match(REGEX_PATTERN, case_filename)
                if match:
                    # 정규식 그룹에서 데이터 추출 (문자열 상태)
                    case_name, lv_str, _, qp_str = match.groups()

                    # 숫자형으로 변환 (히트맵 축 정렬을 위해 중요)
                    lv = int(lv_str)
                    qp = int(qp_str)
                    if qp % 10 != 0:
                        continue
                    print(case_name, lv, qp, vmaf_score)

                    result_data[case_name][lv][qp].append(vmaf_score)

    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        exit()

    return result_data


def calculate_averages(result_data):
    """
    avg_result[case_name][lv][qp] = average_vmaf_score
    """
    avg_result = defaultdict(lambda: defaultdict(lambda: dict))
    avg_result = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))

    for case_name, lv_data in result_data.items():
        for lv, qp_data in lv_data.items():
            for qp, vmaf_list in qp_data.items():
                print(case_name, lv, qp, vmaf_list)
                avg_score = np.mean(vmaf_list)
                avg_result[case_name][lv][qp] = avg_score

    return avg_result


def generate_heatmaps(avg_result, output_dir):
    """
    평균 데이터를 기반으로 각 case_name 별 히트맵을 생성하고 저장합니다.
    X축: QP, Y축: LV
    """
    print(f"Generating heatmaps in directory: {output_dir}...")

    # 출력 디렉토리가 없으면 생성
    os.makedirs(output_dir, exist_ok=True)

    # 시각화 스타일 설정
    sns.set_theme(style="whitegrid")

    for case_name, data_dict in avg_result.items():
        print(f" - Creating heatmap for case: {case_name}")

        # 1. 데이터 변환 (Dict -> Pandas DataFrame)
        # 히트맵을 그리기 위해 데이터를 '긴 형식(Long format)'의 리스트로 만듭니다.
        data_list = []
        for lv, qp_data in data_dict.items():
            for qp, score in qp_data.items():
                data_list.append({'lv': lv, 'qp': qp, 'vmaf': score})

        df = pd.DataFrame(data_list)

        # 2. 피벗 테이블 생성 (히트맵 입력용 행렬 구조 만들기)
        # index=Y축(lv), columns=X축(qp), values=값(vmaf)
        # LV를 역순으로 정렬하여 높은 LV가 위쪽에 오도록 함 (선택사항, 보기 편하게)
        heatmap_data = df.pivot_table(index='lv', columns='qp', values='vmaf').sort_index(ascending=False)
        heatmap_data.index = heatmap_data.index.map(lv_labels)  # LV 레이블 매핑

        # 3. 히트맵 그리기
        plt.figure(figsize=(9, 8)) # 그림 크기 설정

        # vmin, vmax로 색상 범위 고정 (VMAF는 0~100이지만, 데이터 분포에 따라 조정 가능)
        sns.set(font_scale=2.5)
        ax = sns.heatmap(heatmap_data,
                         cmap="Reds",  # 색상 테마 (Yellow-Green-Blue) cmap="YlGnBu"
                         linewidths=.5, vmin=0, vmax=100)

        plt.xlabel('QP', fontsize=30)
        plt.ylabel('RQ', fontsize=30)

        # 4. 파일 저장
        output_filename = os.path.join(output_dir, f'heatmap_{case_name}.pdf')
        plt.savefig(output_filename, dpi=150, bbox_inches='tight')
        plt.close()

    print("All heatmaps generated successfully.")


# === 메인 실행 블록 ===
if __name__ == '__main__':
    # 1단계: 데이터 집계 (result[case][lv][qp] = list)
    aggregated_data = process_and_aggregate_data(INPUT_FILE)

    # 데이터가 비어있으면 종료
    if not aggregated_data:
        print("No valid data found to process.")
        exit()

    # 2단계: 평균 계산 (avg_result[case][lv][qp] = avg_value)
    averaged_data = calculate_averages(aggregated_data)

    # 3단계: 히트맵 생성 및 저장
    generate_heatmaps(averaged_data, OUTPUT_DIR)

