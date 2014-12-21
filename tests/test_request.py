import sys
from threading import Thread

PY2 = sys.version_info[0] == 2
if PY2:
    from SocketServer import TCPServer, BaseRequestHandler
else:
    from socketserver import TCPServer, BaseRequestHandler

import pytest

import overpy

from tests.base_class import read_file

HOST = "127.0.0.1"
PORT_START = 10000
TCPServer.allow_reuse_address = True


class HandleBadRequest(BaseRequestHandler):
    """
    Simulate the response if the query string has syntax errors
    """
    def handle(self):
        self.request.send(b"HTTP/1.0 400 Bad Request\r\n")
        self.request.send(b"Content-Type	text/html; charset=utf-8\r\n")
        self.request.send(b"\r\n")
        self.request.send(read_file("response/bad-request.html", "rb"))


class HandleJSONResponse(BaseRequestHandler):
    """
    """
    def handle(self):
        self.request.send(b"HTTP/1.0 200 OK\r\n")
        self.request.send(b"Content-Type: application/json\r\n")
        self.request.send(b"\r\n")
        self.request.send(read_file("json/way-02.json", "rb"))


class HandleXMLResponse(BaseRequestHandler):
    """
    """
    def handle(self):
        self.request.send(b"HTTP/1.0 200 OK\r\n")
        self.request.send(b"Content-Type: application/osm3s+xml\r\n")
        self.request.send(b"\r\n")
        self.request.send(read_file("xml/way-02.xml", "rb"))


def server_thread(server):
    request = server.get_request()
    server.process_request(*request)
    server.server_close()
    server.socket.close()


class TestQuery(object):
    def test_syntax_error(self):
        port = PORT_START + 1
        server = TCPServer(
            (HOST, port),
            HandleBadRequest
        )
        t = Thread(target=server_thread, args=(server,))
        t.start()

        api = overpy.Overpass()
        api.url = "http://%s:%d" % (HOST, port)
        with pytest.raises(overpy.exception.OverpassBadRequest):
            # Missing ; after way(1)
            api.query((
                "way(1)"
                "out body;"
            ))
        t.join()

    def test_json_response(self):
        port = PORT_START + 2
        server = TCPServer(
            (HOST, port),
            HandleJSONResponse
        )
        t = Thread(target=server_thread, args=(server,))
        t.start()

        api = overpy.Overpass()
        api.url = "http://%s:%d" % (HOST, port)
        result = api.query("[out:json];node(50.745,7.17,50.75,7.18);out;")
        t.join()
        assert len(result.nodes) > 0

    def test_xml_response(self):
        port = PORT_START + 3
        server = TCPServer(
            (HOST, port),
            HandleJSONResponse
        )
        t = Thread(target=server_thread, args=(server,))
        t.start()

        api = overpy.Overpass()
        api.url = "http://%s:%d" % (HOST, port)
        result = api.query("[out:xml];node(50.745,7.17,50.75,7.18);out;")
        t.join()
        assert len(result.nodes) > 0
