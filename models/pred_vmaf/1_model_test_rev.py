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


def model_predict(model, x):
    return model.predict(x)


def create_dir(path):
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError:
        print('Error: creating dir. ' + path)


cam_list = [1,2,3,4,5]
data_root = './loocv/'
model_root = './trained_models/'

for cam in cam_list:
    cam_str = str(cam)
    data_dir = os.path.join(data_root, cam_str)

    training_data = pd.read_csv(os.path.join(data_dir, 'train.csv'), header=0, index_col=False)
    print(training_data.head(5))

    training_dummies = pd.get_dummies(training_data, columns=['codec', 'rq', 'qp']) # for one-hot encoding of categorical variables, starting with codec_, rq_, qp_
    training_features = training_dummies.drop(['vmaf'], axis=1)
    training_vmaf = training_dummies['vmaf']
    print(training_features.columns)

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
        model.fit(training_features.values, training_vmaf.values)
        # train_model(model, training_features.values, training_vmaf.values)

        create_dir(os.path.join('./trained_models', cam_str))
        joblib.dump(model, f"./trained_models/{cam_str}/"+model_key+".pkl")
        # model = joblib.load('your_model.name.pkl')

        for cam2 in cam_list:
            cam2_str = str(cam2)
            testing_data = pd.read_csv(os.path.join(data_root, cam2_str, 'test.csv'), header=0, index_col=False)

            testing_dummies = pd.get_dummies(testing_data, columns=['codec', 'rq', 'qp'])
            testing_features = testing_dummies.drop(['vmaf'], axis=1)
            testing_vmaf = testing_dummies['vmaf']
            print(testing_features.columns)


            y_pred = model_predict(model, testing_features.values)
            err = (abs(y_pred - testing_vmaf.values)).mean()
            dev = (abs(y_pred - testing_vmaf.values)).std()
            np.set_printoptions(precision=3)
            np.set_printoptions(suppress=True)
            mse = ((y_pred - testing_vmaf.values)**2).mean()
            rmse = np.sqrt(mse)
            # print(f"\t\tMSE: {mse:.3f}, error: {err:.3f}")
            print(f"\t{model_key} error: {err:.2f}, dev: {dev:.2f}, rmse: {rmse:.2f}")

            # save model key, error, dev into csv file
            with open(os.path.join("./trained_models/", cam_str, f'model_error_{cam2_str}.csv'), 'a') as f:
                f.write(f"{model_key},{err:.2f},{dev:.2f},{rmse:.2f}\n")

