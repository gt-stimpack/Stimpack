import zmq
import sys
import time
from runtime.common import update_port

def run_client(client_id, qp_value):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)

    socket.setsockopt_string(zmq.IDENTITY, "update_user_qp")
    socket.connect(f"tcp://localhost:{update_port}")

    msg = f"{client_id}:{qp_value}"
    socket.send_string(msg)
    reply = socket.recv()
    print(f"Received reply: {reply.decode()}")

if __name__ == "__main__":
    # input args: update_user_qp.py client_id qp_value
    if len(sys.argv) != 3:
        print("Usage: python update_user_qp.py <client_id> <qp_value>")
        sys.exit(1)
    client_id = int(sys.argv[1])
    qp_value = int(sys.argv[2])
    run_client(client_id, qp_value)
