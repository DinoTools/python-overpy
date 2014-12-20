import pytest

import overpy

from base_class import BaseTestNodes, BaseTestWay
from base_class import read_file


class TestNodes(BaseTestNodes):
    def test_node01(self):
        api = overpy.Overpass()
        result = api.parse_xml(read_file("xml/node-01.xml"))
        self._test_node01(result)


class TestWay(BaseTestWay):
    def test_way01(self):
        api = overpy.Overpass()
        result = api.parse_xml(read_file("xml/way-01.xml"))
        self._test_way01(result)

    def test_way02(self):
        api = overpy.Overpass()
        result = api.parse_xml(read_file("xml/way-02.xml"))
        self._test_way02(result)


class TestDataError(object):
    def _get_element_wrong_type(self):
        data = "<foo></foo>"
        import xml.etree.ElementTree as ET
        return ET.fromstring(data)

    def test_element_wrong_type(self):
        with pytest.raises(overpy.exception.ElementDataWrongType):
            overpy.Node.from_xml(
                self._get_element_wrong_type()
            )

        with pytest.raises(overpy.exception.ElementDataWrongType):
            overpy.Relation.from_xml(
                self._get_element_wrong_type()
            )

        with pytest.raises(overpy.exception.ElementDataWrongType):
            overpy.Way.from_xml(
                self._get_element_wrong_type()
            )