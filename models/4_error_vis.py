import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import csv

matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['ps.fonttype'] = 42
plt.rc('font', size=12)
fig = plt.figure(figsize=(5.5, 4.5), dpi=100)

# 1. 데이터 준비
# read csv file in a list
cam_list = [1,2,3,4,5]
model_list = ['rbf_svr', 'linear_reg', 'sgd_reg', 'voting_reg', 'rf_reg', 'mlp_reg', 'knn_reg', 'dt_reg', 'ada_reg', 'bag_reg']
model_list = ['rbf_svr', 'linear_reg', 'knn_reg', 'dt_reg', 'ada_reg', 'voting_reg']

model_name_for_print = {
    'rbf_svr': 'SVR',
    'linear_reg': 'Linear',
    'knn_reg': 'KNN',
    'dt_reg': 'DT',
    'ada_reg': 'AdaBoost',
    'voting_reg': 'Voting',
    'sgd_reg': 'SGD',
    'rf_reg': 'Random Forest',
    'mlp_reg': 'MLP',
    'bag_reg': 'Bagging'
}

my_colors = ['#4285f4', '#ea4335', '#fbbc04', '#34a853', '#ff6d01', '#46bdc6', '#7baaf7', '#f07b72', '#fcd04f', '#71c287', '#ff994d', '#7ed1d7', '#b3cefb', '#f7b4ae']

csv_dir = './pred_vmaf/trained_models/'

dfs = {}

for model in model_list:
    each_data = []
    for cam in cam_list:
        cam_str = str(cam)
        for cam2 in cam_list:
            cam2_str = str(cam2)
            if cam2 != cam:
               continue
            csv_file = f'{csv_dir}{cam_str}/prediction_error_{cam2_str}_{model}_csvmodule.csv'
            with open(csv_file, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    each_data.append(float(row[0]))  # 첫 번째 열의 값을 float로 변환하여 리스트에 추가

    total_dp = len(each_data)
    df = pd.DataFrame({
        'Model': [model_name_for_print[model]] * total_dp,   # 이름 5개 생성
        'Score': each_data           # 값 5개 매핑
    })
    dfs[model] = df

# draw boxplot for each model
all_df = pd.concat(dfs.values(), ignore_index=True)
sns.boxplot(x='Model', y='Score', data=all_df, width=0.6, palette=my_colors, linewidth=1.5, linecolor='black')

# plt.title(f"Model Performance Comparison", fontsize=16)
plt.ylabel("Prediction Error (RMSE)")
plt.ylim(0, 55)
plt.grid(axis='y', linestyle='--', alpha=0.5) # y축
# plt.show()
fig.savefig('cv_models.pdf', bbox_inches='tight')

