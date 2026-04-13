import threading
from runtime.frame_quality_model import Frame_Quality_Model

class User_Info():
    # given
    id = 0
    codec = ''
    cq = -1

    # from stimpack plugin
    avg_fl = -1
    fl_window = []
    slo_fl = 33.333 # 30 FPS
    fl_port = -1
    rq_port = -1

    # from stimpack runtime
    rq = 0
    rq_history = [[0, -1]] # [rq, rq_round]


    def __init__(self, id=0, codec='h264', cq=10, rq=0, avg_fl=-1, slo_fl=33.333,
            fl_port=-1, rq_port=-1, fl_socket=None, rq_socket=None):
        self.id        = id
        self.codec     = codec
        self.cq        = cq
        self.rq        = rq
        self.avg_fl    = avg_fl
        self.slo_fl    = slo_fl
        self.fl_port   = fl_port
        self.rq_port   = rq_port
        self.fl_socket = fl_socket
        self.rq_socket = rq_socket


    def record_rq(self, rq, round):
        self.rq_history.append([rq, round])
        if len(self.rq_history) > 2:
            self.rq_history.pop(0)


    def print_info(self):
        print(f"User info -- {self.id}")
        print(f"\tCodec -- {self.codec}")
        print(f"\tCompression Quality -- {self.cq}")
        print(f"\tRendering Quality -- {self.rq}")
        print(f"\tRecent Frame Latency Avg -- {self.avg_fl}")
        print(f"\tSLO - Frame Latency -- {self.slo_fl}")
        print(f"\t\tFL IPC Port -- {self.fl_port}")
        print(f"\t\tRQ IPC Port -- {self.rq_port}")


    def print_info_simple(self):
        print(f"User({self.id}), Codec({self.codec}), CQ ({self.cq}), RQ ({self.rq}), avgFL({self.avg_fl}), SLO_FL({self.slo_fl})")
        print(f"RQ History ({self.rq_history})")
        print(f"\tFL_Port ({self.fl_port}), RQ_Port ({self.rq_port})")


    def get_user_info_message(self):
        avg_fps = round(1000.0 / self.avg_fl if self.avg_fl > 0 else -1.0, 2)
        return f"User {self.id} (CQ {self.cq}) \tcurRQ ({self.rq}) \tavgFPS({avg_fps})"


    def update_runtime_info(self, updated_user_info):
        self.rq = updated_user_info.rq
        self.rq_history = updated_user_info.rq_history



user_infos = []
user_infos_lock = threading.Lock()
fl_wnd_size = 3
server_port = 10000
update_port = 11000
rq_adjustment_period = 5
fq_model = Frame_Quality_Model("dt_reg", False)

backoff_switch = 1
backoff_base = 2
backoff_count_max = 3

fps_upper = 120
fps_buffer = 8

promote_weight = 0.5 # VQ score weight
demote_weight  = 0.5 # VQ score weight
