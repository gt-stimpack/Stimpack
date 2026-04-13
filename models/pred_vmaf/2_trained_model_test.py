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


def case_to_string(case):
    # codec = case[0]
    codec = 'H264'
    rq = case[1:5]
    qp = case[5:]

    if rq[0] == 1:
        rq = '0'
    elif rq[1] == 1:
        rq = '1'
    elif rq[2] == 1:
        rq = '2'
    elif rq[3] == 1:
        rq = '3'

    if qp[0] == 1:
        qp = '5'
    elif qp[1] == 1:
        qp = '10'
    elif qp[2] == 1:
        qp = '15'
    elif qp[3] == 1:
        qp = '20'
    elif qp[4] == 1:
        qp = '25'
    elif qp[5] == 1:
        qp = '30'
    elif qp[6] == 1:
        qp = '35'
    elif qp[7] == 1:
        qp = '40'
    elif qp[8] == 1:
        qp = '45'
    elif qp[9] == 1:
        qp = '50'

    return f"{codec}, {rq}, {qp}"



# model test
cases = [
 # codec_h264 only, rq_0,1,2,3, qp_5,10,15,20,25,30,35,40,45,50
    # RQ 0
    [1,  1, 0, 0, 0,  1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1,  1, 0, 0, 0,  0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [1,  1, 0, 0, 0,  0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [1,  1, 0, 0, 0,  0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1,  1, 0, 0, 0,  0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [1,  1, 0, 0, 0,  0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [1,  1, 0, 0, 0,  0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [1,  1, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [1,  1, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [1,  1, 0, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 1],

    # RQ 1
    [1,  0, 1, 0, 0,  1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1,  0, 1, 0, 0,  0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [1,  0, 1, 0, 0,  0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [1,  0, 1, 0, 0,  0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1,  0, 1, 0, 0,  0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [1,  0, 1, 0, 0,  0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [1,  0, 1, 0, 0,  0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [1,  0, 1, 0, 0,  0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [1,  0, 1, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [1,  0, 1, 0, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 1],

    # RQ 2
    [1,  0, 0, 1, 0,  1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1,  0, 0, 1, 0,  0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [1,  0, 0, 1, 0,  0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [1,  0, 0, 1, 0,  0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1,  0, 0, 1, 0,  0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [1,  0, 0, 1, 0,  0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [1,  0, 0, 1, 0,  0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [1,  0, 0, 1, 0,  0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [1,  0, 0, 1, 0,  0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [1,  0, 0, 1, 0,  0, 0, 0, 0, 0, 0, 0, 0, 0, 1],

    # RQ 3
    [1,  0, 0, 0, 1,  1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [1,  0, 0, 0, 1,  0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    [1,  0, 0, 0, 1,  0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    [1,  0, 0, 0, 1,  0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [1,  0, 0, 0, 1,  0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
    [1,  0, 0, 0, 1,  0, 0, 0, 0, 0, 1, 0, 0, 0, 0],
    [1,  0, 0, 0, 1,  0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    [1,  0, 0, 0, 1,  0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [1,  0, 0, 0, 1,  0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    [1,  0, 0, 0, 1,  0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
]

model_dict = {}
model_dict['rbf_svr']    = joblib.load('./trained_models/rbf_svr.pkl')
model_dict['linear_reg'] = joblib.load('./trained_models/linear_reg.pkl')
model_dict['sgd_reg']    = joblib.load('./trained_models/sgd_reg.pkl')
model_dict['voting_reg'] = joblib.load('./trained_models/voting_reg.pkl')
model_dict['rf_reg']     = joblib.load('./trained_models/rf_reg.pkl')
model_dict['mlp_reg']    = joblib.load('./trained_models/mlp_reg.pkl')
model_dict['knn_reg']    = joblib.load('./trained_models/knn_reg.pkl')
model_dict['dt_reg']     = joblib.load('./trained_models/dt_reg.pkl')
model_dict['ada_reg']    = joblib.load('./trained_models/ada_reg.pkl')
model_dict['bag_reg']    = joblib.load('./trained_models/bag_reg.pkl')

# save csv
with open('model_result_test.csv', 'w') as f:
    f.write("model_key, codec, rq, qp, vmaf\n")
    for model_key in model_dict:
        for case in cases:
            model = model_dict[model_key]
            y_pred = model.predict([case])
            print(f"{model_key}, {case_to_string(case)}, frame_quality: {y_pred}")
            f.write(f"{model_key}, {case_to_string(case)}, {y_pred[0]}\n")

