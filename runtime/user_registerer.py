import threading
import zmq
from runtime.fl_monitor import FL_Monitor

from runtime.common import server_port
from runtime.common import user_infos_lock
from runtime.common import User_Info
from runtime.common import user_infos

class User_Registerer(threading.Thread):
    def __init__(self):
        super().__init__()
        self.current_user = 0
        self.base_port = server_port

        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REP)
        self.socket.bind("tcp://*:" + str(self.base_port))


    def run(self):
        while True:
            print("\n[User_Registerer] Listening...")
            codec_cq_message = self.socket.recv()
            print(f"Received from Client: {codec_cq_message}")

            self.current_user += 1

            user_port = self.base_port + (self.current_user*2)

            # decode request -- codec/cq/slo_fl as bytes
            codec = codec_cq_message[:4].decode()
            cq_str     = codec_cq_message[4:6].decode()
            slo_fl_str = codec_cq_message[6:].decode()

            cq = int(cq_str)
            slo_fl = int(slo_fl_str)

            print(f"Client {self.current_user}: codec {codec}, cq {cq}, SLO_fl {slo_fl}")

            # Reply FL_Port / RQ_Port
            self.socket.send(str(user_port).encode())
            ack = self.socket.recv()
            self.socket.send(str(user_port+1).encode())

            fl_socket = self.context.socket(zmq.PULL)
            fl_socket.setsockopt(zmq.CONFLATE, 1)
            fl_socket.connect("tcp://localhost:" + str(user_port))

            rq_socket = self.context.socket(zmq.REQ)
            rq_socket.connect("tcp://localhost:" + str(user_port+1))

            # Table update
            user_infos_lock.acquire()
            user_info = User_Info(id=self.current_user, codec=codec, cq=cq, rq=0, avg_fl=-1, slo_fl=slo_fl,
                                  fl_port=user_port, rq_port=user_port+1,
                                  fl_socket=fl_socket, rq_socket=rq_socket)
            user_infos.append(user_info)
            user_infos_lock.release()

            ut = FL_Monitor(self.current_user)
            ut.start()

