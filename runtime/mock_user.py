import zmq
import time
import numpy as np
import threading

context = zmq.Context()

class FL_Reporter(threading.Thread):
    def __init__(self, fl_port):
        super().__init__()
        self.fl_socket = context.socket(zmq.PUSH)
        self.fl_socket.bind("tcp://*:" + str(fl_port))

    def run(self):
        while True:
            fl = np.random.randint(5, 40)
            msg = fl.to_bytes(4, "little")
            print(f"Recent FL: {fl} ms")
            self.fl_socket.send(msg)
            time.sleep(1)


class RQ_Listener(threading.Thread):
    def __init__(self, rq_port):
        super().__init__()
        self.rq_socket = context.socket(zmq.REP)
        self.rq_socket.bind("tcp://*:" + str(rq_port))

    def run(self):
        while True:
            rq = self.rq_socket.recv()
            rq_val = rq[0]
            print(f"current RQ: {rq_val}")
            self.rq_socket.send(b'ack')


#  Socket to talk to server
print("Connecting to server…")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:10000")

fl_port = 0
rq_port = 0
fl_socket = None
rq_socket = None

# Set four clients
socket.send(b"h26406032") # h264 (codec) + 00 (cq) + 000 (SLO_FL in ms)

#  Get the reply.
message = socket.recv()
fl_port = message.decode()
socket.send(b"ack")
message = socket.recv()
rq_port = message.decode()

print(f"FL_port ({fl_port}), RQ_port ({rq_port})")

rq_listener_thread = RQ_Listener(rq_port)
rq_listener_thread.start()

fl_reporter_thread = FL_Reporter(fl_port)
fl_reporter_thread.start()

rq_listener_thread.join()
fl_reporter_thread.join()

