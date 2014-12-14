from decimal import Decimal
import os

import overpy


def read_file(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    return open(filename).read()


class TestNodes(object):
    def test_node01(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/node-01.json"))

        assert len(result.nodes) == 3
        assert len(result.relations) == 0
        assert len(result.ways) == 0

        node = result.nodes[0]

        assert isinstance(node, overpy.Node)
        assert isinstance(node.id, int)
        assert isinstance(node.lat, Decimal)
        assert isinstance(node.lon, Decimal)
        assert node.id == 50878400
        assert node.lat == Decimal("50.7461788")
        assert node.lon == Decimal("7.1742257")

        assert isinstance(node.tags, dict)
        assert len(node.tags) == 0

        node = result.nodes[1]

        assert isinstance(node, overpy.Node)
        assert isinstance(node.id, int)
        assert isinstance(node.lat, Decimal)
        assert isinstance(node.lon, Decimal)
        assert node.id == 100793192
        assert node.lat == Decimal("50.7468472")
        assert node.lon == Decimal("7.1709376")

        assert isinstance(node.tags, dict)
        assert len(node.tags) == 1

        assert node.tags["highway"] == "turning_circle"

        node = result.nodes[2]
        assert isinstance(node, overpy.Node)
        assert isinstance(node.id, int)
        assert isinstance(node.lat, Decimal)
        assert isinstance(node.lon, Decimal)
        assert node.id == 3233854234
        assert node.lat == Decimal("50.7494236")
        assert node.lon == Decimal("7.1757664")

        assert isinstance(node.attributes, dict)
        assert len(node.attributes) == 5
        assert node.attributes["changeset"] == 23456789
        assert node.attributes["user"] == "TestUser"


class TestWay(object):
    def test_way01(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/way-01.json"))

        assert len(result.nodes) == 0
        assert len(result.relations) == 0
        assert len(result.ways) == 2

        way = result.ways[0]

        assert isinstance(way, overpy.Way)
        assert isinstance(way.id, int)
        assert way.id == 317146077

        assert isinstance(way.tags, dict)
        assert len(way.tags) == 1
        assert way.tags["building"] == "yes"

        assert isinstance(way.attributes, dict)
        print(way.attributes)
        assert len(way.attributes) == 0

        way = result.ways[1]

        assert isinstance(way, overpy.Way)
        assert isinstance(way.id, int)
        assert way.id == 317146078

        assert isinstance(way.tags, dict)
        assert len(way.tags) == 0

        assert isinstance(way.attributes, dict)
        assert len(way.attributes) == 5

        assert way.attributes["uid"] == 345678
        assert way.attributes["user"] == "TestUser"
        assert way.attributes["changeset"] == 23456789


    def test_way02(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/way-02.json"))

        assert len(result.nodes) == 6
        assert len(result.relations) == 0
        assert len(result.ways) == 1

        node = result.nodes[0]

        assert isinstance(node, overpy.Node)
        assert isinstance(node.id, int)
        assert isinstance(node.lat, Decimal)
        assert isinstance(node.lon, Decimal)
        assert node.id == 3233854233
        assert node.lat == Decimal("50.7494187")
        assert node.lon == Decimal("7.1758731")

        way = result.ways[0]

        assert isinstance(way, overpy.Way)
        assert isinstance(way.id, int)
        assert way.id == 317146077

        assert isinstance(way.tags, dict)
        assert len(way.tags) == 1
        assert way.tags["building"] == "yes"

        nodes = way.nodes

        assert len(nodes) == 7

        node = nodes[0]

        assert isinstance(node, overpy.Node)
        assert node.id == 3233854241