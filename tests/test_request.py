from http.server import BaseHTTPRequestHandler

import pytest

import overpy

from tests import read_file, new_server_thread, stop_server_thread


def handle_bad_request(request):
    request.send_response(400, "Bad Request")
    request.send_header("Content-Type", "text/html; charset=utf-8")
    request.end_headers()
    request.wfile.write(read_file("response/bad-request.html", "rb"))


def handle_bad_request_encoding(request):
    request.send_response(400, "Bad Request")
    request.send_header("Content-Type", "text/html; charset=utf-8")
    request.end_headers()
    request.wfile.write(read_file("response/bad-request-encoding.html", "rb"))


def handle_too_many_requests(request):
    request.send_response(429, "Too Many Requests")
    request.send_header("Content-Type", "text/html; charset=utf-8")
    request.end_headers()
    request.wfile.write(b"Too Many Requests")


def handle_gateway_timeout(request):
    request.send_response(504, "Gateway Timeout")
    request.send_header("Content-Type", "text/html; charset=utf-8")
    request.end_headers()
    request.wfile.write(b"Gateway Timeout")


def handle_unknown_content_type(request):
    request.send_response(200, "OK")
    request.send_header("Content-Type", "application/foobar")
    request.end_headers()
    request.wfile.write(read_file("xml/way-02.xml", "rb"))


def handle_unknown_http_status_code(request):
    request.send_response(123, "Unknown")
    request.send_header("Content-Type", "text/html; charset=utf-8")
    request.end_headers()
    request.wfile.write(b"Unknown status code")


class HandleOverpassBadRequest(BaseHTTPRequestHandler):
    """
    Simulate the response if the query string has syntax errors
    """
    def do_POST(self):
        handle_bad_request(self)


class HandleOverpassBadRequestEncoding(BaseHTTPRequestHandler):
    """
    """
    def do_POST(self):
        handle_bad_request_encoding(self)


class HandleOverpassTooManyRequests(BaseHTTPRequestHandler):
    """
    """
    def do_POST(self):
        handle_too_many_requests(self)


class HandleOverpassGatewayTimeout(BaseHTTPRequestHandler):
    """
    """
    def do_POST(self):
        handle_gateway_timeout(self)


class HandleOverpassUnknownHTTPStatusCode(BaseHTTPRequestHandler):
    """
    """
    def do_POST(self):
        handle_unknown_http_status_code(self)


class HandleResponseJSON(BaseHTTPRequestHandler):
    """
    """
    def do_POST(self):
        self.send_response(200, "OK")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(read_file("json/way-02.json", "rb"))


class HandleResponseXML(BaseHTTPRequestHandler):
    """
    """
    def do_POST(self):
        self.send_response(200, "OK")
        self.send_header("Content-Type", "application/osm3s+xml")
        self.end_headers()
        self.wfile.write(read_file("xml/way-02.xml", "rb"))


class HandleResponseUnknown(BaseHTTPRequestHandler):
    """
    """
    def do_POST(self):
        handle_unknown_content_type(self)


class HandleRetry(BaseHTTPRequestHandler):
    default_handler_func = [
        handle_bad_request,
        handle_bad_request_encoding,
        handle_too_many_requests,
        handle_gateway_timeout,
        handle_unknown_content_type,
        handle_unknown_http_status_code
    ]

    def do_POST(self):
        f = self.default_handler_func.pop(0)
        f(self)


class TestQuery:
    def test_chunk_size(self):
        url, server = new_server_thread(HandleResponseJSON)

        api = overpy.Overpass(read_chunk_size=128)
        api.url = url
        result = api.query("[out:json];node(50.745,7.17,50.75,7.18);out;")
        stop_server_thread(server)
        assert len(result.nodes) > 0

    def test_overpass_syntax_error(self):
        url, server = new_server_thread(HandleOverpassBadRequest)

        api = overpy.Overpass()
        api.url = url
        with pytest.raises(overpy.exception.OverpassBadRequest):
            # Missing ; after way(1)
            api.query(
                "way(1)"
                "out body;"
            )
        stop_server_thread(server)

    def test_overpass_syntax_error_encoding_error(self):
        with pytest.raises(UnicodeDecodeError):
            # File should be encoded with iso8859-15 and will raise an exception
            tmp = read_file("response/bad-request-encoding.html", "rb")
            tmp.decode("utf-8")

        url, server = new_server_thread(HandleOverpassBadRequestEncoding)

        api = overpy.Overpass()
        api.url = url
        with pytest.raises(overpy.exception.OverpassBadRequest):
            # Missing ; after way(1)
            api.query(
                "way(1)"
                "out body;"
            )
        stop_server_thread(server)

    def test_overpass_too_many_requests(self):
        url, server = new_server_thread(HandleOverpassTooManyRequests)

        api = overpy.Overpass()
        api.url = url
        with pytest.raises(overpy.exception.OverpassTooManyRequests):
            api.query(
                "way(1);"
                "out body;"
            )
        stop_server_thread(server)

    def test_overpass_gateway_timeout(self):
        url, server = new_server_thread(HandleOverpassGatewayTimeout)

        api = overpy.Overpass()
        api.url = url
        with pytest.raises(overpy.exception.OverpassGatewayTimeout):
            api.query(
                "way(1);"
                "out body;"
            )
        stop_server_thread(server)

    def test_overpass_unknown_status_code(self):
        url, server = new_server_thread(HandleOverpassUnknownHTTPStatusCode)

        api = overpy.Overpass()
        api.url = url
        with pytest.raises(overpy.exception.OverpassUnknownHTTPStatusCode):
            api.query(
                "way(1);"
                "out body;"
            )
        stop_server_thread(server)

    def test_response_json(self):
        url, server = new_server_thread(HandleResponseJSON)

        api = overpy.Overpass()
        api.url = url
        result = api.query("[out:json];node(50.745,7.17,50.75,7.18);out;")
        stop_server_thread(server)
        assert len(result.nodes) > 0

    def test_response_unknown(self):
        url, server = new_server_thread(HandleResponseUnknown)

        api = overpy.Overpass()
        api.url = url
        with pytest.raises(overpy.exception.OverpassUnknownContentType):
            api.query("[out:xml];node(50.745,7.17,50.75,7.18);out;")
        stop_server_thread(server)

    def test_response_xml(self):
        url, server = new_server_thread(HandleResponseXML)

        api = overpy.Overpass()
        api.url = url
        result = api.query("[out:xml];node(50.745,7.17,50.75,7.18);out;")
        stop_server_thread(server)
        assert len(result.nodes) > 0

    def test_retry(self):
        url, server = new_server_thread(HandleRetry)

        api = overpy.Overpass()
        # HandleRetry.default_handler_cls should contain at least 2 classes to process
        api.max_retry_count = len(HandleRetry.default_handler_func) - 1
        api.url = url
        with pytest.raises(overpy.exception.MaxRetriesReached):
            api.query(
                "way(1);"
                "out body;"
            )
        stop_server_thread(server)
