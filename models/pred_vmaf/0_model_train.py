import os
import pandas as pd
import numpy as np
import warnings
import joblib

from sklearn.preprocessing   import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn import model_selection

from sklearn.linear_model    import LogisticRegression
from sklearn.linear_model    import LinearRegression
from sklearn.linear_model    import SGDRegressor
from sklearn.svm             import SVR
from sklearn.svm             import LinearSVR
from sklearn.svm             import NuSVR
from sklearn.neighbors       import KNeighborsRegressor
from sklearn.tree            import DecisionTreeRegressor
from sklearn.tree            import ExtraTreeRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.neural_network  import MLPRegressor
from sklearn.ensemble        import RandomForestRegressor
from sklearn.ensemble        import AdaBoostRegressor
from sklearn.ensemble        import GradientBoostingRegressor
from sklearn.ensemble        import BaggingRegressor
from sklearn.ensemble        import ExtraTreesRegressor
from sklearn.ensemble        import StackingRegressor
from sklearn.ensemble        import VotingRegressor


def train_model(model, x, y):
    model.fit(x, y)


def model_predict(model, x):
    return model.predict(x)


def print_arr_info(name, arr):
    print(f"{name}: mean {arr.mean():.3f}, std {arr.std():.3f}")


def create_dir(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        print('Error: creating dir. ' + path)


def save_prediction_error_by_cq(ref, pred, cq_wnd=5):
    error = abs(ref - pred)
    rq_index = 0
    results = {}
    for cq_idx in range(0, len(ref), cq_wnd):
        rq_index %= 4
        cur_rq = ''
        if rq_index == 0: # Low
            cur_rq = 'Low'
        if rq_index == 1: # Medium
            cur_rq = 'Medium'
        if rq_index == 2: # High
            cur_rq = 'High'
        if rq_index == 3: # Very High
            cur_rq = 'Very High'
        rq_index += 1

        results[f"{cur_rq} + "] = error[cq_idx:cq_idx+cq_wnd].mean()
        print(f"cq_{cq_idx}, {cur_rq}: mean {error[cq_idx:cq_idx+cq_wnd].mean():.3f}, std {error[cq_idx:cq_idx+cq_wnd].std():.3f}")
        # print(cq_idx, end=', ')
        None

training_data = pd.read_csv("./training_data.csv", header=0, index_col=False)
testing_data = pd.read_csv("./testing_data.csv", header=0, index_col=False)
# data = data[['rendering_quality', 'compression_quality', 'dss', 'fsim', 'haarpsi', 'mdsi', 'ms_ssim', 'vif', 'vsi', 'sr_sim']]

print("==================== Training Data Profile =====================")
print('codec: \n\n', training_data['codec'].value_counts())
print('rendering_quality: \n\n', training_data['rq'].value_counts())
print('compression_quality: \n\n', training_data['qp'].value_counts())
print("================================================================")
# print("===================== Testing Data Profile =====================")
# print('codec: \n\n', testing_data['codec'].value_counts())
# print('rendering_quality: \n\n', testing_data['rendering_quality'].value_counts())
# print('compression_quality: \n\n', testing_data['compression_quality'].value_counts())
# print("================================================================")

training_dummies = pd.get_dummies(training_data, columns=['codec', 'rq', 'qp'])
training_features = training_dummies.drop(['vmaf'], axis=1)
training_vmaf = training_dummies['vmaf']
# print features for checking order
print(training_features.columns)

testing_dummies = pd.get_dummies(training_data, columns=['codec', 'rq', 'qp'])
testing_features = testing_dummies.drop(['vmaf'], axis=1)
testing_vmaf = testing_dummies['vmaf']

logistic_reg = LogisticRegression()
linear_reg  = LinearRegression()
sgd_reg = SGDRegressor()
rbf_svr = SVR(kernel='rbf', gamma='auto')
linear_svr  = SVR(kernel='linear')
nu_svr = NuSVR()
knn_reg = KNeighborsRegressor()
dt_reg = DecisionTreeRegressor()
et_reg = ExtraTreeRegressor()
gp_reg = GaussianProcessRegressor()
mlp_reg = MLPRegressor()
rf_reg = RandomForestRegressor()
ada_reg = AdaBoostRegressor()
gb_reg = GradientBoostingRegressor()
bag_reg = BaggingRegressor()
et_reg = ExtraTreesRegressor()
stack_reg = StackingRegressor(estimators=[('rbf_svr', rbf_svr), ('linear_svr', linear_svr), ('linear_reg', linear_reg), ('sgd_reg', sgd_reg)])
voting_reg = VotingRegressor(estimators=[('rbf_svr', rbf_svr), ('linear_svr', linear_svr), ('linear_reg', linear_reg), ('sgd_reg', sgd_reg)])

model_dict = {}
model_dict['rbf_svr'] = rbf_svr
model_dict['linear_reg'] = linear_reg
model_dict['sgd_reg'] = sgd_reg
model_dict['voting_reg'] = voting_reg
model_dict['rf_reg'] = rf_reg
model_dict['mlp_reg'] = mlp_reg
model_dict['knn_reg'] = knn_reg
model_dict['dt_reg'] = dt_reg
model_dict['ada_reg'] = ada_reg
model_dict['bag_reg'] = bag_reg

for model_key in model_dict:
    model = model_dict[model_key]
    train_model(model, training_features.values, training_vmaf.values)

    create_dir('./trained_models')
    joblib.dump(model, "./trained_models/"+model_key+".pkl")
    # model = joblib.load('your_model.name.pkl')

    y_pred = model_predict(model, testing_features.values)
    # print(y_pred)
    # print(features.columns)
    # print(x_test[0])
    # print_arr_info("\t\tPred", y_pred)
    # print_arr_info("\t\tActual", testing_metric_dict[metric_key])
    # mse = ((y_pred - testing_metric_dict[metric_key])**2).mean()
    err = (abs(y_pred - testing_vmaf.values)).mean()
    dev = (abs(y_pred - testing_vmaf.values)).std()
    np.set_printoptions(precision=3)
    np.set_printoptions(suppress=True)
    mse = ((y_pred - testing_vmaf.values)**2).mean()
    rmse = np.sqrt(mse)
    # save_prediction_error_by_cq(testing_metric_dict[metric_key], y_pred)
    # print(f"\t\tMSE: {mse:.3f}, error: {err:.3f}")
    print(f"\t{model_key} error: {err}, dev: {dev:.3f}, rmse: {rmse:.3f}")

    # save model key, error, dev into csv file
    with open('model_error.csv', 'a') as f:
        f.write(f"{model_key},{err:.3f},{dev:.3f},{rmse:.3f}\n")

