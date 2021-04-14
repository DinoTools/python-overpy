from http.server import BaseHTTPRequestHandler

import pytest

import overpy

from tests import read_file, new_server_thread, stop_server_thread
from tests.base_class import BaseTestWay


class HandleResponseJSON02(BaseHTTPRequestHandler):
    """
    """
    def do_POST(self):
        self.send_response(200, "OK")
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(read_file("json/result-expand-02.json", "rb"))


class TestResult:
    def test_expand_error(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/result-expand-01.json"))
        with pytest.raises(ValueError):
            result.expand(123)
        with pytest.raises(ValueError):
            result.expand(1.23)
        with pytest.raises(ValueError):
            result.expand("abc")

    def test_expand_01(self):
        api = overpy.Overpass()
        result1 = api.parse_json(read_file("json/result-expand-01.json"))

        assert len(result1.nodes) == 2
        assert len(result1.ways) == 1

        result2 = api.parse_json(read_file("json/result-expand-02.json"))

        assert len(result2.nodes) == 2
        assert len(result2.ways) == 1

        result1.expand(result2)

        # Don't overwrite existing elements
        assert len(result1.nodes) == 3
        assert len(result1.ways) == 2


class TestArea:
    def test_missing_unresolvable(self):
        url, server = new_server_thread(HandleResponseJSON02)

        api = overpy.Overpass()
        api.url = url
        result1 = api.parse_json(read_file("json/result-expand-01.json"))

        with pytest.raises(overpy.exception.DataIncomplete):
            result1.get_area(123, resolve_missing=True)
        stop_server_thread(server)

    def test_missing_resolvable(self):
        url, server = new_server_thread(HandleResponseJSON02)

        api = overpy.Overpass()
        api.url = url
        result1 = api.parse_json(read_file("json/result-expand-01.json"))

        # Node must not be available
        with pytest.raises(overpy.exception.DataIncomplete):
            result1.get_area(3605945176)

        # Node must be available
        area = result1.get_area(3605945176, resolve_missing=True)

        assert isinstance(area, overpy.Area)
        assert area.id == 3605945176

        stop_server_thread(server)


class TestNode:
    def test_missing_unresolvable(self):
        url, server = new_server_thread(HandleResponseJSON02)

        api = overpy.Overpass()
        api.url = url
        result1 = api.parse_json(read_file("json/result-expand-01.json"))

        with pytest.raises(overpy.exception.DataIncomplete):
            result1.get_node(123, resolve_missing=True)
        stop_server_thread(server)

    def test_missing_resolvable(self):
        url, server = new_server_thread(HandleResponseJSON02)

        api = overpy.Overpass()
        api.url = url
        result1 = api.parse_json(read_file("json/result-expand-01.json"))

        # Node must not be available
        with pytest.raises(overpy.exception.DataIncomplete):
            result1.get_node(3233854235)

        # Node must be available
        node = result1.get_node(3233854235, resolve_missing=True)

        assert isinstance(node, overpy.Node)
        assert node.id == 3233854235

        stop_server_thread(server)


class TestPickle(BaseTestWay):
    def test_way02(self):
        """
        Try to pickle and unpickle the result object
        """
        import pickle

        api = overpy.Overpass()
        result = api.parse_json(read_file("json/way-02.json"))
        self._test_way02(result)
        # do pickle and unpickle
        result_string = pickle.dumps(result)
        new_result = pickle.loads(result_string)
        # test new result
        self._test_way02(new_result)


class TestRelation:
    def test_missing_unresolvable(self):
        url, server = new_server_thread(HandleResponseJSON02)

        api = overpy.Overpass()
        api.url = url
        result1 = api.parse_json(read_file("json/result-expand-01.json"))

        with pytest.raises(overpy.exception.DataIncomplete):
            result1.get_relation(123, resolve_missing=True)
        stop_server_thread(server)

    def test_missing_resolvable(self):
        url, server = new_server_thread(HandleResponseJSON02)

        api = overpy.Overpass()
        api.url = url
        result1 = api.parse_json(read_file("json/result-expand-01.json"))

        # Relation must not be available
        with pytest.raises(overpy.exception.DataIncomplete):
            result1.get_relation(2046898)

        # Relation must be available
        relation = result1.get_relation(2046898, resolve_missing=True)

        assert isinstance(relation, overpy.Relation)
        assert relation.id == 2046898

        stop_server_thread(server)


class TestWay:
    def test_missing_unresolvable(self):
        url, server = new_server_thread(HandleResponseJSON02)

        api = overpy.Overpass()
        api.url = url
        result1 = api.parse_json(read_file("json/result-expand-01.json"))

        with pytest.raises(overpy.exception.DataIncomplete):
            result1.get_way(123, resolve_missing=True)
        stop_server_thread(server)

    def test_missing_resolvable(self):
        url, server = new_server_thread(HandleResponseJSON02)

        api = overpy.Overpass()
        api.url = url
        result1 = api.parse_json(read_file("json/result-expand-01.json"))

        # Way must not be available
        with pytest.raises(overpy.exception.DataIncomplete):
            result1.get_way(317146078)

        # Way must be available
        way = result1.get_way(317146078, resolve_missing=True)

        assert isinstance(way, overpy.Way)
        assert way.id == 317146078

        stop_server_thread(server)
