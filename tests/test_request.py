import pytest

import overpy

from tests import OverpyBaseRequestHandler
from tests import read_file, new_server_thread, server_thread_retry


class HandleOverpassBadRequest(OverpyBaseRequestHandler):
    """
    Simulate the response if the query string has syntax errors
    """
    @staticmethod
    def get_response(self):
        yield b"HTTP/1.0 400 Bad Request\r\n"
        yield b"Content-Type	text/html; charset=utf-8\r\n"
        yield b"\r\n"
        yield read_file("response/bad-request.html", "rb")


class HandleOverpassBadRequestEncoding(OverpyBaseRequestHandler):
    """
    """
    @staticmethod
    def get_response(self):
        yield b"HTTP/1.0 400 Bad Request\r\n"
        yield b"Content-Type	text/html; charset=utf-8\r\n"
        yield b"\r\n"
        yield read_file("response/bad-request-encoding.html", "rb")


class HandleOverpassTooManyRequests(OverpyBaseRequestHandler):
    """
    """
    @staticmethod
    def get_response(self):
        yield b"HTTP/1.0 429 Too Many Requests\r\n"
        yield b"Content-Type	text/html; charset=utf-8\r\n"
        yield b"\r\n"
        yield b"Too Many Requests"


class HandleOverpassGatewayTimeout(OverpyBaseRequestHandler):
    """
    """
    @staticmethod
    def get_response(self):
        yield b"HTTP/1.0 504 Gateway Timeout\r\n"
        yield b"Content-Type	text/html; charset=utf-8\r\n"
        yield b"\r\n"
        yield b"Gateway Timeout"


class HandleOverpassUnknownHTTPStatusCode(OverpyBaseRequestHandler):
    """
    """
    @staticmethod
    def get_response(self):
        yield b"HTTP/1.0 123 Unknown\r\n"
        yield b"Content-Type	text/html; charset=utf-8\r\n"
        yield b"\r\n"
        yield b"Unknown status code"


class HandleResponseJSON(OverpyBaseRequestHandler):
    """
    """
    @staticmethod
    def get_response(self):
        yield b"HTTP/1.0 200 OK\r\n"
        yield b"Content-Type: application/json\r\n"
        yield b"\r\n"
        yield read_file("json/way-02.json", "rb")


class HandleResponseXML(OverpyBaseRequestHandler):
    """
    """
    @staticmethod
    def get_response(self):
        yield b"HTTP/1.0 200 OK\r\n"
        yield b"Content-Type: application/osm3s+xml\r\n"
        yield b"\r\n"
        yield read_file("xml/way-02.xml", "rb")


class HandleResponseUnknown(OverpyBaseRequestHandler):
    """
    """
    @staticmethod
    def get_response(self):
        yield b"HTTP/1.0 200 OK\r\n"
        yield b"Content-Type: application/foobar\r\n"
        yield b"\r\n"
        yield read_file("xml/way-02.xml", "rb")


class HandleRetry(OverpyBaseRequestHandler):
    default_handler_cls = [
        HandleOverpassBadRequest,
        HandleOverpassBadRequestEncoding,
        HandleOverpassTooManyRequests,
        HandleOverpassGatewayTimeout,
        HandleOverpassUnknownHTTPStatusCode,
        HandleResponseUnknown
    ]

    @staticmethod
    def get_response(self):
        h = self.default_handler_cls.pop(0)
        return h.get_response(self)


class TestQuery(object):
    def test_chunk_size(self):
        url, t = new_server_thread(HandleResponseJSON)

        api = overpy.Overpass(read_chunk_size=128)
        api.url = url
        result = api.query("[out:json];node(50.745,7.17,50.75,7.18);out;")
        t.join()
        assert len(result.nodes) > 0

    def test_overpass_syntax_error(self):
        url, t = new_server_thread(HandleOverpassBadRequest)

        api = overpy.Overpass()
        api.url = url
        with pytest.raises(overpy.exception.OverpassBadRequest):
            # Missing ; after way(1)
            api.query((
                "way(1)"
                "out body;"
            ))
        t.join()

    def test_overpass_syntax_error_encoding_error(self):
        with pytest.raises(UnicodeDecodeError):
            # File should be encoded with iso8859-15 and will raise an exception
            tmp = read_file("response/bad-request-encoding.html", "rb")
            tmp.decode("utf-8")

        url, t = new_server_thread(HandleOverpassBadRequestEncoding)

        api = overpy.Overpass()
        api.url = url
        with pytest.raises(overpy.exception.OverpassBadRequest):
            # Missing ; after way(1)
            api.query((
                "way(1)"
                "out body;"
            ))
        t.join()

    def test_overpass_too_many_requests(self):
        url, t = new_server_thread(HandleOverpassTooManyRequests)

        api = overpy.Overpass()
        api.url = url
        with pytest.raises(overpy.exception.OverpassTooManyRequests):
            api.query((
                "way(1);"
                "out body;"
            ))
        t.join()

    def test_overpass_gateway_timeout(self):
        url, t = new_server_thread(HandleOverpassGatewayTimeout)

        api = overpy.Overpass()
        api.url = url
        with pytest.raises(overpy.exception.OverpassGatewayTimeout):
            api.query((
                "way(1);"
                "out body;"
            ))
        t.join()

    def test_overpass_unknown_status_code(self):
        url, t = new_server_thread(HandleOverpassUnknownHTTPStatusCode)

        api = overpy.Overpass()
        api.url = url
        with pytest.raises(overpy.exception.OverpassUnknownHTTPStatusCode):
            api.query((
                "way(1);"
                "out body;"
            ))
        t.join()

    def test_response_json(self):
        url, t = new_server_thread(HandleResponseJSON)

        api = overpy.Overpass()
        api.url = url
        result = api.query("[out:json];node(50.745,7.17,50.75,7.18);out;")
        t.join()
        assert len(result.nodes) > 0

    def test_response_unknown(self):
        url, t = new_server_thread(HandleResponseUnknown)

        api = overpy.Overpass()
        api.url = url
        with pytest.raises(overpy.exception.OverpassUnknownContentType):
            api.query("[out:xml];node(50.745,7.17,50.75,7.18);out;")
        t.join()

    def test_response_xml(self):
        url, t = new_server_thread(HandleResponseXML)

        api = overpy.Overpass()
        api.url = url
        result = api.query("[out:xml];node(50.745,7.17,50.75,7.18);out;")
        t.join()
        assert len(result.nodes) > 0

    def test_retry(self):
        url, t = new_server_thread(HandleRetry, handle_func=server_thread_retry)

        api = overpy.Overpass()
        # HandleRetry.default_handler_cls should contain at least 2 classes to process
        api.max_retry_count = len(HandleRetry.default_handler_cls) - 1
        api.url = url
        with pytest.raises(overpy.exception.MaxRetriesReached):
            api.query((
                "way(1);"
                "out body;"
            ))
        t.join()
