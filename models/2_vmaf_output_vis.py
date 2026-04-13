import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. CSV 파일 읽기
df = pd.read_csv('output_cam.csv')

# 2. 그래프 스타일 설정
sns.set_theme(style="whitegrid")
plt.figure(figsize=(10, 6))

# 3. 선 그래프 그리기
# x축: QP (압축률), y축: VMAF (화질)
# hue: 'rq'를 기준으로 선 색깔을 다르게 구분 (범례 표시)
# marker: 각 데이터 포인트를 점으로 표시
sns.lineplot(data=df, x='qp', y='vmaf', hue='rq', marker='o', palette='viridis')

# 4. 그래프 꾸미기
plt.title('VMAF Score vs QP by RQ Setting', fontsize=16)
plt.xlabel('QP (Quantization Parameter)', fontsize=12)
plt.ylabel('VMAF Score', fontsize=12)
plt.ylim(0, 100)  # VMAF는 보통 0~100 사이이므로 범위 고정
plt.legend(title='RQ Type', title_fontsize='12')

# 5. 보여주기 (또는 저장)
plt.tight_layout()
plt.show()
# plt.savefig('vmaf_analysis.png') # 파일로 저장하려면 주석 해제
