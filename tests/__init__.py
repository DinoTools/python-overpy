import os
import sys
import time
from multiprocessing import Process
from threading import Lock

PY2 = sys.version_info[0] == 2
if PY2:
    from SocketServer import TCPServer, BaseRequestHandler
else:
    from socketserver import TCPServer, BaseRequestHandler

TCPServer.allow_reuse_address = True

HOST = "127.0.0.1"
PORT_START = sys.version_info[0] * 10000 + sys.version_info[1] * 100

current_port = PORT_START
test_lock = Lock()


class OverpyBaseRequestHandler(BaseRequestHandler):
    def handle(self):
        for data in self.get_response(self):
            self.request.send(data)

    @staticmethod
    def get_response(self):
        yield b""


def read_file(filename, mode="r"):
    filename = os.path.join(os.path.dirname(__file__), filename)
    return open(filename, mode).read()


def server_thread(server):
    request = server.get_request()
    server.process_request(*request)
    server.server_close()
    server.socket.close()


def server_thread_retry(server):
    from .test_request import HandleRetry
    num_requests = len(HandleRetry.default_handler_cls)
    while num_requests > 0:
        print(num_requests)
        request = server.get_request()
        server.process_request(*request)
        num_requests = num_requests - 1
    server.server_close()
    server.socket.close()


def new_server_thread(handle_cls, handle_func=None, port=None):
    if handle_func is None:
        handle_func = server_thread
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
    p = Process(target=handle_func, args=(server,))
    p.start()
    # Give the server some time to bind
    # Is there a better option?
    time.sleep(0.2)
    return (
        "http://%s:%d" % (HOST, port),
        p
    )
