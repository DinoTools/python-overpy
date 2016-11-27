from decimal import Decimal
from datetime import datetime
import os

import pytest

import overpy

from tests import read_file


class BaseTestAreas(object):
    def _test_area01(self, result):
        assert len(result.areas) == 4
        assert len(result.nodes) == 0
        assert len(result.relations) == 0
        assert len(result.ways) == 0

        area = result.areas[0]

        assert isinstance(area, overpy.Area)
        assert isinstance(area.id, int)
        assert area.id == 2448756446

        assert isinstance(area.tags, dict)
        assert len(area.tags) == 12

        area = result.areas[1]

        assert isinstance(area, overpy.Area)
        assert isinstance(area.id, int)
        assert area.id == 3600055060

        assert isinstance(area.tags, dict)
        assert len(area.tags) == 13

        area = result.areas[2]
        assert isinstance(area, overpy.Area)
        assert isinstance(area.id, int)
        assert area.id == 3605945175

        assert isinstance(area.tags, dict)
        assert len(area.tags) == 12

        area = result.areas[3]
        assert isinstance(area, overpy.Area)
        assert isinstance(area.id, int)
        assert area.id == 3605945176

        assert isinstance(area.tags, dict)
        assert len(area.tags) == 14

        # try to get a single area by id
        area = result.get_area(3605945175)
        assert area.id == 3605945175

        # try to get a single area by id not available in the result
        with pytest.raises(overpy.exception.DataIncomplete):
            result.get_area(123456)

        # area_ids is an alias for get_node_ids() and should return the same data
        for area_ids in (result.area_ids, result.get_area_ids()):
            assert len(area_ids) == 4
            assert area_ids[0] == 2448756446
            assert area_ids[1] == 3600055060
            assert area_ids[2] == 3605945175
            assert area_ids[3] == 3605945176

        assert len(result.node_ids) == 0
        assert len(result.get_node_ids()) == 0

        assert len(result.relation_ids) == 0
        assert len(result.get_relation_ids()) == 0

        assert len(result.way_ids) == 0
        assert len(result.get_way_ids()) == 0


class BaseTestNodes(object):
    def _test_node01(self, result):
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
        assert node.attributes["timestamp"] == datetime(2014, 12, 14, 7, 27, 19, 0, None)
        assert node.attributes["uid"] == 345678
        assert node.attributes["user"] == "TestUser"
        assert node.attributes["version"] == 1

        # try to get a single node by id
        node = result.get_node(50878400)
        assert node.id == 50878400

        # try to get a single node by id not available in the result
        with pytest.raises(overpy.exception.DataIncomplete):
            result.get_node(123456)

        # node_ids is an alias for get_node_ids() and should return the same data
        for node_ids in (result.node_ids, result.get_node_ids()):
            assert len(node_ids) == 3
            assert node_ids[0] == 50878400
            assert node_ids[1] == 100793192
            assert node_ids[2] == 3233854234

        assert len(result.relation_ids) == 0
        assert len(result.get_relation_ids()) == 0

        assert len(result.way_ids) == 0
        assert len(result.get_way_ids()) == 0


class BaseTestRelation(object):
    def _test_relation01(self, result):
        assert len(result.nodes) == 0
        assert len(result.relations) == 1
        assert len(result.ways) == 0

        relation = result.relations[0]

        assert isinstance(relation, overpy.Relation)
        assert isinstance(relation.id, int)
        assert relation.id == 2046898

        assert isinstance(relation.tags, dict)
        assert len(relation.tags) == 6
        assert relation.tags["from"] == "Here"
        assert relation.tags["name"] == "Test relation"
        assert relation.tags["ref"] == "609"
        assert relation.tags["route"] == "bus"
        assert relation.tags["to"] == "There"
        assert relation.tags["type"] == "route"

        assert isinstance(relation.attributes, dict)
        assert len(relation.attributes) == 5

        assert relation.attributes["changeset"] == 17433822
        assert relation.attributes["timestamp"] == datetime(2014, 12, 15, 13, 13, 11, 0, None)
        assert relation.attributes["uid"] == 12345
        assert relation.attributes["user"] == "Username"
        assert relation.attributes["version"] == 12

        assert len(relation.members) == 5
        assert isinstance(relation.members[0], overpy.RelationNode)
        assert isinstance(relation.members[1], overpy.RelationNode)
        assert isinstance(relation.members[2], overpy.RelationNode)
        assert isinstance(relation.members[3], overpy.RelationNode)
        assert isinstance(relation.members[4], overpy.RelationWay)

    def _test_relation02(self, result):
        assert len(result.nodes) == 3
        assert len(result.relations) == 1
        assert len(result.ways) == 1

        relation = result.relations[0]

        assert isinstance(relation, overpy.Relation)
        assert isinstance(relation.id, int)
        assert relation.id == 2046898

        assert isinstance(relation.tags, dict)
        assert len(relation.tags) == 6
        assert relation.tags["from"] == "Here"
        assert relation.tags["name"] == "Test relation"
        assert relation.tags["ref"] == "609"
        assert relation.tags["route"] == "bus"
        assert relation.tags["to"] == "There"
        assert relation.tags["type"] == "route"

        assert isinstance(relation.attributes, dict)
        assert len(relation.attributes) == 5

        assert len(relation.members) == 4

        member = relation.members[0]
        assert isinstance(member, overpy.RelationNode)
        node = member.resolve()
        assert isinstance(node, overpy.Node)
        assert node.id == 3233854233
        assert member.ref == node.id

        member = relation.members[1]
        assert isinstance(member, overpy.RelationNode)
        node = member.resolve()
        assert isinstance(node, overpy.Node)
        assert node.id == 3233854234
        assert member.ref == node.id

        member = relation.members[2]
        assert isinstance(member, overpy.RelationNode)
        node = member.resolve()
        assert isinstance(node, overpy.Node)
        assert node.id == 3233854235
        assert member.ref == node.id

        member = relation.members[3]
        assert isinstance(member, overpy.RelationWay)
        way = member.resolve()
        assert isinstance(way, overpy.Way)
        assert way.id == 317146078
        assert member.ref == way.id

    def _test_relation03(self, result):
        assert len(result.nodes) == 0
        assert len(result.relations) == 1
        assert len(result.ways) == 0

        relation = result.relations[0]

        assert isinstance(relation, overpy.Relation)
        assert isinstance(relation.id, int)
        assert relation.id == 23092

        assert isinstance(relation.tags, dict)
        assert len(relation.tags) == 10

        assert isinstance(relation.center_lat, Decimal)
        assert isinstance(relation.center_lon, Decimal)
        assert relation.center_lat == Decimal("50.8176646")
        assert relation.center_lon == Decimal("7.0208539")

    def _test_relation04(self, result):
        assert len(result.nodes) == 0
        assert len(result.relations) == 1
        assert len(result.ways) == 0

        relation = result.relations[0]

        assert isinstance(relation, overpy.Relation)
        assert isinstance(relation.id, int)
        assert relation.id == 23092

        assert isinstance(relation.tags, dict)
        assert len(relation.tags) == 10

        way = relation.members[2]

        assert isinstance(way, overpy.RelationWay)
        assert len(way.attributes) == 0
        assert isinstance(way.attributes, dict)

        assert isinstance(way.geometry, list)
        assert len(way.geometry) == 2
        assert isinstance(way.geometry[0], overpy.RelationWayGeometryValue)
        assert isinstance(way.geometry[0].lat, Decimal)
        assert isinstance(way.geometry[0].lon, Decimal)
        assert way.geometry[0].lat == Decimal("50.8137408")
        assert way.geometry[0].lon == Decimal("6.9813352")


class BaseTestWay(object):
    def _test_way01(self, result):
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
        assert len(way.attributes) == 0

        way = result.ways[1]

        assert isinstance(way, overpy.Way)
        assert isinstance(way.id, int)
        assert way.id == 317146078

        assert isinstance(way.tags, dict)
        assert len(way.tags) == 0

        assert isinstance(way.attributes, dict)
        assert len(way.attributes) == 5

        assert way.attributes["changeset"] == 23456789
        assert way.attributes["timestamp"] == datetime(2014, 12, 14, 7, 27, 21, 0, None)
        assert way.attributes["uid"] == 345678
        assert way.attributes["user"] == "TestUser"
        assert way.attributes["version"] == 1

        # try to get a single way by id
        way = result.get_way(317146077)
        assert way.id == 317146077

        # try to get a single way by id not available in the result
        with pytest.raises(overpy.exception.DataIncomplete):
            result.get_way(123456)

        assert len(result.node_ids) == 0
        assert len(result.get_node_ids()) == 0

        assert len(result.relation_ids) == 0
        assert len(result.get_relation_ids()) == 0

        # way_ids is an alias for get_way_ids() and should return the same data
        for way_ids in (result.way_ids, result.get_way_ids()):
            assert len(way_ids) == 2
            assert way_ids[0] == 317146077
            assert way_ids[1] == 317146078

    def _test_way02(self, result):
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

        # try to get a single way by id
        way = result.get_way(317146077)
        assert way.id == 317146077

        # try to get a single way by id not available in the result
        with pytest.raises(overpy.exception.DataIncomplete):
            result.get_way(123456)

        # node_ids is an alias for get_node_ids() and should return the same data
        for node_ids in (result.node_ids, result.get_node_ids()):
            assert len(node_ids) == 6
            assert node_ids[0] == 3233854233
            assert node_ids[1] == 3233854234
            assert node_ids[2] == 3233854236
            assert node_ids[3] == 3233854237
            assert node_ids[4] == 3233854238
            assert node_ids[5] == 3233854241

        assert len(result.relation_ids) == 0
        assert len(result.get_relation_ids()) == 0

        # way_ids is an alias for get_way_ids() and should return the same data
        for way_ids in (result.way_ids, result.get_way_ids()):
            assert len(way_ids) == 1
            assert way_ids[0] == 317146077

    def _test_way03(self, result):
        assert len(result.nodes) == 4
        assert len(result.relations) == 0
        assert len(result.ways) == 1

        way = result.ways[0]

        assert isinstance(way, overpy.Way)
        assert isinstance(way.id, int)
        assert way.id == 225576797

        assert isinstance(way.tags, dict)
        assert len(way.tags) == 2
        assert way.tags["building"] == "kiosk"
        assert way.tags["shop"] == "florist"

        assert isinstance(way.center_lat, Decimal)
        assert isinstance(way.center_lon, Decimal)
        assert way.center_lat == Decimal("41.8954998")
        assert way.center_lon == Decimal("12.5032265")

        for nodes in (way.nodes, way.get_nodes()):
            assert len(nodes) == 5
            for node in nodes:
                assert isinstance(node, overpy.Node)
                assert isinstance(node.id, int)

            assert nodes[0].id == 2343425525
            assert nodes[1].id == 2343425528
            assert nodes[2].id == 2343425526
            assert nodes[3].id == 2343425523
            assert nodes[4].id == 2343425525

        # try to get a single way by id
        way = result.get_way(225576797)
        assert way.id == 225576797

        # try to get a single way by id not available in the result
        with pytest.raises(overpy.exception.DataIncomplete):
            result.get_way(123456)

        # node_ids is an alias for get_node_ids() and should return the same data
        for node_ids in (result.node_ids, result.get_node_ids()):
            assert len(node_ids) == 4
            assert node_ids[0] == 2343425523
            assert node_ids[1] == 2343425525
            assert node_ids[2] == 2343425526
            assert node_ids[3] == 2343425528

        assert len(result.relation_ids) == 0
        assert len(result.get_relation_ids()) == 0

        # way_ids is an alias for get_way_ids() and should return the same data
        for way_ids in (result.way_ids, result.get_way_ids()):
            assert len(way_ids) == 1
            assert way_ids[0] == 225576797
