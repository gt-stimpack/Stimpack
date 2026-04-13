import threading
import time
import zmq

from runtime.common import update_port
from runtime.common import user_infos_lock
from runtime.common import User_Info
from runtime.common import user_infos

class User_QP_Updater(threading.Thread):
    def __init__(self):
        super().__init__()
        self.update_port = update_port
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.socket.bind(f"tcp://*:{str(self.update_port)}")

    def run(self):
        while True:
            time.sleep(0.1)
            try:
                # packet structure of recv_multipart: [identity][empty][data] -- empty is a delimiter
                packet = self.socket.recv_multipart()
                identity = packet[0]  # client identifier
                msg = packet[2].decode('utf-8')  # data
                msg_parts = msg.split(':')
                user_id = int(msg_parts[0])
                new_qp = int(msg_parts[1])
                print(f"Received update from User {user_id}: New CQ = {new_qp}")

                # Send ACK back to client -- identity must be included -- id + ACK
                response_packet = packet[:-1] + [b"ACK"]
                self.socket.send_multipart(response_packet)

                # Table update
                user_infos_lock.acquire()
                for user_info in user_infos:
                    if user_info.id == user_id:
                        user_info.cq = new_qp
                        print(f"Updated User {user_id} CQ to {new_qp}")
                        break
                user_infos_lock.release()
            except zmq.Again:
                continue
            except Exception as e:
                print(f"Error: {e}")

