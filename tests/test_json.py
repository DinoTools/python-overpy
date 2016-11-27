import pytest

import overpy

from tests.base_class import BaseTestAreas, BaseTestNodes, BaseTestRelation, BaseTestWay
from tests.base_class import read_file


class TestAreas(BaseTestAreas):
    def test_area01(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/area-01.json"))
        self._test_area01(result)


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

    def test_relation03(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/relation-03.json"))
        self._test_relation03(result)

    def test_relation04(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/relation-04.json"))
        self._test_relation04(result)


class TestWay(BaseTestWay):
    def test_way01(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/way-01.json"))
        self._test_way01(result)

    def test_way02(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/way-02.json"))
        self._test_way02(result)

    def test_way03(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/way-03.json"))
        self._test_way03(result)

    def test_way04(self):
        api = overpy.Overpass()
        with pytest.raises(ValueError):
            api.parse_json(read_file("json/way-04.json"))


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