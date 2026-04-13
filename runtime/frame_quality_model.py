from sklearn.svm import SVR
from statistics import fmean
import joblib
import os, pyprojroot
from runtime.mock_model import MockModel

class Frame_Quality_Model():
    def __init__(self, model, mock=False):
        if mock:
            self.name = "mock"
            self.vmaf_model = MockModel()
            return

        self.name = model
        proj_dir = pyprojroot.find_root(pyprojroot.has_dir(".git"))
        model_to_load = os.path.join(proj_dir, 'models/pred_vmaf/trained_models', model + ".pkl")
        print(f"Loading model from {model_to_load}")
        self.vmaf_model = joblib.load(model_to_load)


    def encode_features(self, codec, rq, cq):
        codec_ohe = [1] # 'h264'
        rq_ohe = [0, 0, 0, 0] # '0', '1', '2', '3'
        cq_ohe = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0] # '5', '10', '15', '20', '25', '30', '35', '40', '45', '50'

        if rq == 0: # low
            rq_ohe = [1, 0, 0, 0]
        elif rq == 1: # medium
            rq_ohe = [0, 1, 0, 0]
        elif rq == 2: # high
            rq_ohe = [0, 0, 1, 0]
        elif rq == 3: # very high
            rq_ohe = [0, 0, 0, 1]

        if cq <= 5:
            cq_ohe = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        elif cq <= 10:
            cq_ohe = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        elif cq <= 15:
            cq_ohe = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
        elif cq <= 20:
            cq_ohe = [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
        elif cq <= 25:
            cq_ohe = [0, 0, 0, 0, 1, 0, 0, 0, 0, 0]
        elif cq <= 30:
            cq_ohe = [0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
        elif cq <= 35:
            cq_ohe = [0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
        elif cq <= 40:
            cq_ohe = [0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
        elif cq <= 45:
            cq_ohe = [0, 0, 0, 0, 0, 0, 0, 0, 1, 0]
        else:
            cq_ohe = [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
        return codec_ohe, rq_ohe, cq_ohe


    def predict_fq(self, codec, rq, cq):
        codec_ohe, rq_ohe, cq_ohe = self.encode_features(codec, rq, cq)
        features = [codec_ohe + rq_ohe + cq_ohe]
        pred = self.vmaf_model.predict(features)
        return pred[0]

