from decimal import Decimal
import os

import pytest

import overpy

from tests import read_file


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
        # ToDo: fix
        # assert node.attributes["changeset"] == 23456789
        # assert node.attributes["user"] == "TestUser"

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

        # ToDo: fix it
        # assert way.attributes["uid"] == 345678
        # assert way.attributes["user"] == "TestUser"
        # assert way.attributes["changeset"] == 23456789

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