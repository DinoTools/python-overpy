from http.server import BaseHTTPRequestHandler

import pytest

import overpy

from tests import read_file, new_server_thread, stop_server_thread


class HandleResponseJSON01(BaseHTTPRequestHandler):
    """
    """
    def do_POST(self):
        self.send_response(200, "OK")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(read_file("json/result-way-01.json", "rb"))


class HandleResponseJSON02(BaseHTTPRequestHandler):
    """
    """
    def do_POST(self):
        self.send_response(200, "OK")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(read_file("json/result-way-02.json", "rb"))


class HandleResponseJSON03(BaseHTTPRequestHandler):
    """
    """
    def do_POST(self):
        self.send_response(200, "OK")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(read_file("json/result-way-03.json", "rb"))


class TestNodes:
    def test_missing_unresolvable(self):
        url, server = new_server_thread(HandleResponseJSON01)

        api = overpy.Overpass()
        api.url = url
        result = api.parse_json(read_file("json/result-way-01.json"))

        assert len(result.nodes) == 0
        assert len(result.ways) == 1

        way = result.ways[0]
        assert isinstance(way, overpy.Way)

        with pytest.raises(overpy.exception.DataIncomplete):
            way.get_nodes()

        with pytest.raises(overpy.exception.DataIncomplete):
            way.get_nodes(resolve_missing=True)

        assert len(result.nodes) == 0
        stop_server_thread(server)

    def test_missing_partly_unresolvable(self):
        url, server = new_server_thread(HandleResponseJSON02)

        api = overpy.Overpass()
        api.url = url
        result = api.parse_json(read_file("json/result-way-01.json"))

        assert len(result.nodes) == 0
        assert len(result.ways) == 1

        way = result.ways[0]
        assert isinstance(way, overpy.Way)

        with pytest.raises(overpy.exception.DataIncomplete):
            way.get_nodes()

        with pytest.raises(overpy.exception.DataIncomplete):
            way.get_nodes(resolve_missing=True)

        assert len(result.nodes) == 1
        stop_server_thread(server)

    def test_missing_resolvable(self):
        url, server = new_server_thread(HandleResponseJSON03)

        api = overpy.Overpass()
        api.url = url
        result = api.parse_json(read_file("json/result-way-01.json"))

        assert len(result.nodes) == 0
        assert len(result.ways) == 1

        way = result.ways[0]
        assert isinstance(way, overpy.Way)

        with pytest.raises(overpy.exception.DataIncomplete):
            way.get_nodes()

        nodes = way.get_nodes(resolve_missing=True)

        assert len(nodes) == 2

        stop_server_thread(server)
