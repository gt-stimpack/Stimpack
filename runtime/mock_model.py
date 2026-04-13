import numpy as np

class MockModel():
#    vh_pred = [
#        91.03,
#        79.36,
#        48.56,
#    ]
#    h_pred = [
#        78.50,
#        69.60,
#        43.98,
#    ]
#    m_pred = [
#        58.05,
#        53.39,
#        35.49,
#    ]
#    l_pred = [
#        27.7,
#        23.92,
#        18.9,
#    ]
    # 10, 15, 25
    # 9,  12, 20
    # 4,  6,  10
    vh_pred = [
        80.0,
        77.0,
        45.0
    ]
    h_pred = [
        65.0,
        60.0,
        44.0
    ]
    m_pred = [
        50.0,
        47.0,
        38.0
    ]
    l_pred = [
        24.0 ,
        22.0 ,
        16.0
    ]



    # features = [1] + [0, 0, 1, 0] + [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]: codec + rq + cq
    def predict(self, features):
        # print(f"features: {features}")
        features = features[0]
        codec = features[0]
        rq = features[1:5]
        cq = features[5:-1]
        # print(codec, rq, cq)

        cq_index = 0
        if cq[0] or cq[1] or cq[2]:
            cq_index = 0
        elif cq[5] or cq[6]:
            cq_index = 1
        else:
            cq_index = 2
        # print(f"cq_index: {cq_index}")

        if rq[0]:
            return [self.l_pred[cq_index]]
        elif rq[1]:
            return [self.m_pred[cq_index]]
        elif rq[2]:
            return [self.h_pred[cq_index]]
        else:
            return [self.vh_pred[cq_index]]




if __name__ == "__main__":
    mock_model = MockModel()

    _codec = [True]
    _rq = [False, False, False, True]
    _qp = [False, False, False, False, False, True, False, False, False, False]
    _features = np.array([_codec + _rq + _qp])

    pred = mock_model.predict(_features)
    print(f"pred: {pred}")
