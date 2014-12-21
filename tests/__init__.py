import os
import sys
from threading import Thread, Lock

PY2 = sys.version_info[0] == 2
if PY2:
    from SocketServer import TCPServer, BaseRequestHandler
else:
    from socketserver import TCPServer, BaseRequestHandler

TCPServer.allow_reuse_address = True

HOST = "127.0.0.1"
PORT_START = 10000

current_port = PORT_START
test_lock = Lock()


def read_file(filename, mode="r"):
    filename = os.path.join(os.path.dirname(__file__), filename)
    return open(filename, mode).read()


def server_thread(server):
    request = server.get_request()
    server.process_request(*request)
    server.server_close()
    server.socket.close()


def new_server_thread(handle_cls, port=None):
    global current_port
    if port is None:
        test_lock.acquire()
        port = current_port
        current_port += 1
        test_lock.release()

    server = TCPServer(
        (HOST, port),
        handle_cls
    )
    return (
        "http://%s:%d" % (HOST, port),
        Thread(target=server_thread, args=(server,))
    )