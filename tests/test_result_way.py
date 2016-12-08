import pytest

import overpy

from tests import read_file, new_server_thread, BaseRequestHandler


class HandleResponseJSON01(BaseRequestHandler):
    """
    """
    def handle(self):
        self.request.send(b"HTTP/1.0 200 OK\r\n")
        self.request.send(b"Content-Type: application/json\r\n")
        self.request.send(b"\r\n")
        self.request.send(read_file("json/result-way-01.json", "rb"))


class HandleResponseJSON02(BaseRequestHandler):
    """
    """
    def handle(self):
        self.request.send(b"HTTP/1.0 200 OK\r\n")
        self.request.send(b"Content-Type: application/json\r\n")
        self.request.send(b"\r\n")
        self.request.send(read_file("json/result-way-02.json", "rb"))


class HandleResponseJSON03(BaseRequestHandler):
    """
    """
    def handle(self):
        self.request.send(b"HTTP/1.0 200 OK\r\n")
        self.request.send(b"Content-Type: application/json\r\n")
        self.request.send(b"\r\n")
        self.request.send(read_file("json/result-way-03.json", "rb"))


class TestNodes(object):
    def test_missing_unresolvable(self):
        url, t = new_server_thread(HandleResponseJSON01)

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
        t.join()

    def test_missing_partly_unresolvable(self):
        url, t = new_server_thread(HandleResponseJSON02)

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
        t.join()

    def test_missing_resolvable(self):
        url, t = new_server_thread(HandleResponseJSON03)

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

        t.join()