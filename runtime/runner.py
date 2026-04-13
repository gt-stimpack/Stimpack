import zmq
import time
import threading
import common
import sys
from runtime.user_registerer import User_Registerer
from runtime.user_qp_updater import User_QP_Updater
from runtime.rq_manager import RQ_Manager
from runtime.common import fq_model
from runtime.my_logger import My_Logger

if __name__ == "__main__":
    print("[Rendering quality manager] START")
    # input arguments #1 log file name #2 case name
    if len(sys.argv) > 1:
        my_logger = My_Logger(sys.argv[1], sys.argv[2])
    else:
        print("No log file name and case name provided, you can provide them as arguments")
        my_logger = My_Logger()

    print(f"[START!] RQ round period({common.rq_adjustment_period}s), alpah({common.demote_weight})/beta({common.promote_weight})")
    print(f"\tbackoff_switch({common.backoff_switch}), backoff_count_max({common.backoff_count_max}), fps_upper({common.fps_upper}), model({fq_model.name})")

    user_registerer_thread = User_Registerer()
    user_registerer_thread.start()

    user_qp_updater_thread = User_QP_Updater()
    user_qp_updater_thread.start()

    rq_manager_thread = RQ_Manager(fq_model, logger=my_logger)
    rq_manager_thread.start()

    user_registerer_thread.join()
    user_qp_updater_thread.join()
    rq_manager_thread.join()
    print("[Rendering quality manager] END")
