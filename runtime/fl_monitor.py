import threading
import zmq
import time
from statistics import mean
import runtime.common as common
from runtime.common import user_infos
from runtime.common import User_Info
from runtime.common import fl_wnd_size

class FL_Monitor(threading.Thread):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.this_user = User_Info()
        self.avg_fl = -1
        self.fl_window = []

        for user_info in user_infos:
            if user_info.id == self.id:
                self.this_user = user_info

        self.socket = self.this_user.fl_socket
        print(f"User {self.id} FL monitor ON")
        print(f"\tFL port: {self.this_user.fl_port}")


    def run(self):
        while True:
            time.sleep(0.5)
            message = self.socket.recv()
            # print(message)
            fl = int.from_bytes(message, "little")


            if len(self.fl_window) >= fl_wnd_size:
                del self.fl_window[0]

            self.fl_window.append(fl)
            self.avg_fl = round(mean(self.fl_window), 2)
            # print(f"\tuser({self.this_user.id}) RQ({self.this_user.rq}) SLO({self.this_user.slo_fl}) avg FL: {self.this_user.avg_fl}->{self.avg_fl}ms, {self.fl_window}")

            common.user_infos_lock.acquire()
            self.this_user.avg_fl = self.avg_fl
            self.this_user.fl_window = self.fl_window
            common.user_infos_lock.release()

