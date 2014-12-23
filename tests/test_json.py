import pytest

import overpy

from tests.base_class import BaseTestNodes, BaseTestRelation, BaseTestWay
from tests.base_class import read_file


class TestNodes(BaseTestNodes):
    def test_node01(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/node-01.json"))
        self._test_node01(result)


class TestRelation(BaseTestRelation):
    def test_relation01(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/relation-01.json"))
        self._test_relation01(result)

    def test_relation02(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/relation-02.json"))
        self._test_relation02(result)


class TestWay(BaseTestWay):
    def test_way01(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/way-01.json"))
        self._test_way01(result)

    def test_way02(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/way-02.json"))
        self._test_way02(result)


class TestDataError(object):
    def test_element_wrong_type(self):
        with pytest.raises(overpy.exception.ElementDataWrongType):
            overpy.Node.from_json(
                {
                    "type": "foo"
                }
            )

        with pytest.raises(overpy.exception.ElementDataWrongType):
            overpy.Relation.from_json(
                {
                    "type": "foo"
                }
            )

        with pytest.raises(overpy.exception.ElementDataWrongType):
            overpy.RelationNode.from_json(
                {
                    "type": "foo"
                }
            )

        with pytest.raises(overpy.exception.ElementDataWrongType):
            overpy.RelationWay.from_json(
                {
                    "type": "foo"
                }
            )
        with pytest.raises(overpy.exception.ElementDataWrongType):
            overpy.Way.from_json(
                {
                    "type": "foo"
                }
            )