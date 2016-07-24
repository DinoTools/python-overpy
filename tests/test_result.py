import pytest
from datetime import datetime

import overpy

from tests import read_file, new_server_thread, BaseRequestHandler


class HandleResponseJSON02(BaseRequestHandler):
    """
    """
    def handle(self):
        self.request.send(b"HTTP/1.0 200 OK\r\n")
        self.request.send(b"Content-Type: application/json\r\n")
        self.request.send(b"\r\n")
        self.request.send(read_file("json/result-expand-02.json", "rb"))


class TestResult(object):
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

class TestAttributesConversion(object):
    def test_attribute_conversion(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/way-meta.json"))

        for o in result.ways + result.nodes:
            assert(type(o.attributes['uid']) == int)
            assert(type(o.attributes['changeset']) == int)
            assert(type(o.attributes['version']) == int)
            assert(type(o.attributes['user']) == unicode)
            assert(type(o.attributes['timestamp']) == datetime)



class TestNode(object):
    def test_missing_unresolvable(self):
        url, t = new_server_thread(HandleResponseJSON02)
        t.start()

        api = overpy.Overpass()
        api.url = url
        result1 = api.parse_json(read_file("json/result-expand-01.json"))

        with pytest.raises(overpy.exception.DataIncomplete):
            result1.get_node(123, resolve_missing=True)
        t.join()

    def test_missing_resolvable(self):
        url, t = new_server_thread(HandleResponseJSON02)
        t.start()

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

        t.join()


class TestRelation(object):
    def test_missing_unresolvable(self):
        url, t = new_server_thread(HandleResponseJSON02)
        t.start()

        api = overpy.Overpass()
        api.url = url
        result1 = api.parse_json(read_file("json/result-expand-01.json"))

        with pytest.raises(overpy.exception.DataIncomplete):
            result1.get_relation(123, resolve_missing=True)
        t.join()

    def test_missing_resolvable(self):
        url, t = new_server_thread(HandleResponseJSON02)
        t.start()

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

        t.join()


class TestWay(object):
    def test_missing_unresolvable(self):
        url, t = new_server_thread(HandleResponseJSON02)
        t.start()

        api = overpy.Overpass()
        api.url = url
        result1 = api.parse_json(read_file("json/result-expand-01.json"))

        with pytest.raises(overpy.exception.DataIncomplete):
            result1.get_way(123, resolve_missing=True)
        t.join()

    def test_missing_resolvable(self):
        url, t = new_server_thread(HandleResponseJSON02)
        t.start()

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

        t.join()

# vim: set ts=4 et :

