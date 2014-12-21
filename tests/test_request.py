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


class HandleOverpassBadRequest(BaseRequestHandler):
    """
    Simulate the response if the query string has syntax errors
    """
    def handle(self):
        self.request.send(b"HTTP/1.0 400 Bad Request\r\n")
        self.request.send(b"Content-Type	text/html; charset=utf-8\r\n")
        self.request.send(b"\r\n")
        self.request.send(read_file("response/bad-request.html", "rb"))


class HandleOverpassTooManyRequests(BaseRequestHandler):
    """
    """
    def handle(self):
        self.request.send(b"HTTP/1.0 429 Too Many Requests\r\n")
        self.request.send(b"Content-Type	text/html; charset=utf-8\r\n")
        self.request.send(b"\r\n")
        self.request.send(b"Too Many Requests")


class HandleOverpassGatewayTimeout(BaseRequestHandler):
    """
    """
    def handle(self):
        self.request.send(b"HTTP/1.0 504 Gateway Timeout\r\n")
        self.request.send(b"Content-Type	text/html; charset=utf-8\r\n")
        self.request.send(b"\r\n")
        self.request.send(b"Gateway Timeout")


class HandleOverpassUnknownHTTPStatusCode(BaseRequestHandler):
    """
    """
    def handle(self):
        self.request.send(b"HTTP/1.0 123 Unknown\r\n")
        self.request.send(b"Content-Type	text/html; charset=utf-8\r\n")
        self.request.send(b"\r\n")
        self.request.send(b"Unknown status code")


class HandleResponseJSON(BaseRequestHandler):
    """
    """
    def handle(self):
        self.request.send(b"HTTP/1.0 200 OK\r\n")
        self.request.send(b"Content-Type: application/json\r\n")
        self.request.send(b"\r\n")
        self.request.send(read_file("json/way-02.json", "rb"))


class HandleResponseXML(BaseRequestHandler):
    """
    """
    def handle(self):
        self.request.send(b"HTTP/1.0 200 OK\r\n")
        self.request.send(b"Content-Type: application/osm3s+xml\r\n")
        self.request.send(b"\r\n")
        self.request.send(read_file("xml/way-02.xml", "rb"))


class HandleResponseUnknown(BaseRequestHandler):
    """
    """
    def handle(self):
        self.request.send(b"HTTP/1.0 200 OK\r\n")
        self.request.send(b"Content-Type: application/foobar\r\n")
        self.request.send(b"\r\n")
        self.request.send(read_file("xml/way-02.xml", "rb"))


def server_thread(server):
    request = server.get_request()
    server.process_request(*request)
    server.server_close()
    # server.socket.close()


class TestQuery(object):
    def test_overpass_syntax_error(self):
        port = PORT_START + 1
        server = TCPServer(
            (HOST, port),
            HandleOverpassBadRequest
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

    def test_overpass_too_many_requests(self):
        port = PORT_START + 1
        server = TCPServer(
            (HOST, port),
            HandleOverpassTooManyRequests
        )
        t = Thread(target=server_thread, args=(server,))
        t.start()

        api = overpy.Overpass()
        api.url = "http://%s:%d" % (HOST, port)
        with pytest.raises(overpy.exception.OverpassTooManyRequests):
            api.query((
                "way(1);"
                "out body;"
            ))
        t.join()

    def test_overpass_gateway_timeout(self):
        port = PORT_START + 1
        server = TCPServer(
            (HOST, port),
            HandleOverpassGatewayTimeout
        )
        t = Thread(target=server_thread, args=(server,))
        t.start()

        api = overpy.Overpass()
        api.url = "http://%s:%d" % (HOST, port)
        with pytest.raises(overpy.exception.OverpassGatewayTimeout):
            api.query((
                "way(1);"
                "out body;"
            ))
        t.join()

    def test_overpass_unknown_status_code(self):
        port = PORT_START + 1
        server = TCPServer(
            (HOST, port),
            HandleOverpassUnknownHTTPStatusCode
        )
        t = Thread(target=server_thread, args=(server,))
        t.start()

        api = overpy.Overpass()
        api.url = "http://%s:%d" % (HOST, port)
        with pytest.raises(overpy.exception.OverpassUnknownHTTPStatusCode):
            api.query((
                "way(1);"
                "out body;"
            ))
        t.join()

    def test_response_json(self):
        port = PORT_START + 2
        server = TCPServer(
            (HOST, port),
            HandleResponseJSON
        )
        t = Thread(target=server_thread, args=(server,))
        t.start()

        api = overpy.Overpass()
        api.url = "http://%s:%d" % (HOST, port)
        result = api.query("[out:json];node(50.745,7.17,50.75,7.18);out;")
        t.join()
        assert len(result.nodes) > 0

    def test_response_unknown(self):
        port = PORT_START + 3
        server = TCPServer(
            (HOST, port),
            HandleResponseUnknown
        )
        t = Thread(target=server_thread, args=(server,))
        t.start()

        api = overpy.Overpass()
        api.url = "http://%s:%d" % (HOST, port)
        with pytest.raises(overpy.exception.OverpassUnknownContentType):
            api.query("[out:xml];node(50.745,7.17,50.75,7.18);out;")
        t.join()

    def test_response_xml(self):
        port = PORT_START + 3
        server = TCPServer(
            (HOST, port),
            HandleResponseXML
        )
        t = Thread(target=server_thread, args=(server,))
        t.start()

        api = overpy.Overpass()
        api.url = "http://%s:%d" % (HOST, port)
        result = api.query("[out:xml];node(50.745,7.17,50.75,7.18);out;")
        t.join()
        assert len(result.nodes) > 0