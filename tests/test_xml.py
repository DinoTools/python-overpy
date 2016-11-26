import pytest

import overpy

from tests.base_class import BaseTestAreas, BaseTestNodes, BaseTestRelation, BaseTestWay
from tests.base_class import read_file


class TestAreas(BaseTestAreas):
    def test_node01(self):
        api = overpy.Overpass()
        # DOM
        result = api.parse_xml(read_file("xml/area-01.xml"), parser=overpy.XML_PARSER_DOM)
        self._test_area01(result)
        # SAX
        result = api.parse_xml(read_file("xml/area-01.xml"), parser=overpy.XML_PARSER_SAX)
        self._test_area01(result)


class TestNodes(BaseTestNodes):
    def test_node01(self):
        api = overpy.Overpass()
        # DOM
        result = api.parse_xml(read_file("xml/node-01.xml"), parser=overpy.XML_PARSER_DOM)
        self._test_node01(result)
        # SAX
        result = api.parse_xml(read_file("xml/node-01.xml"), parser=overpy.XML_PARSER_SAX)
        self._test_node01(result)


class TestRelation(BaseTestRelation):
    def test_relation01(self):
        api = overpy.Overpass()
        # DOM
        result = api.parse_xml(read_file("xml/relation-01.xml"), parser=overpy.XML_PARSER_DOM)
        self._test_relation01(result)
        # SAX
        result = api.parse_xml(read_file("xml/relation-01.xml"), parser=overpy.XML_PARSER_SAX)
        self._test_relation01(result)

    def test_relation02(self):
        api = overpy.Overpass()
        # DOM
        result = api.parse_xml(read_file("xml/relation-02.xml"), parser=overpy.XML_PARSER_DOM)
        self._test_relation02(result)
        # SAX
        result = api.parse_xml(read_file("xml/relation-02.xml"), parser=overpy.XML_PARSER_SAX)
        self._test_relation02(result)

    def test_relation03(self):
        api = overpy.Overpass()
        # DOM
        result = api.parse_xml(read_file("xml/relation-03.xml"), parser=overpy.XML_PARSER_DOM)
        self._test_relation03(result)
        # SAX
        result = api.parse_xml(read_file("xml/relation-03.xml"), parser=overpy.XML_PARSER_SAX)
        self._test_relation03(result)

    def test_relation04(self):
        api = overpy.Overpass()
        # DOM
        result = api.parse_xml(read_file("xml/relation-04.xml"), parser=overpy.XML_PARSER_DOM)
        self._test_relation04(result)
        # SAX
        result = api.parse_xml(read_file("xml/relation-04.xml"), parser=overpy.XML_PARSER_SAX)
        self._test_relation04(result)


class TestWay(BaseTestWay):
    def test_way01(self):
        api = overpy.Overpass()
        # DOM
        result = api.parse_xml(read_file("xml/way-01.xml"), parser=overpy.XML_PARSER_DOM)
        self._test_way01(result)
        # SAX
        result = api.parse_xml(read_file("xml/way-01.xml"), parser=overpy.XML_PARSER_SAX)
        self._test_way01(result)

    def test_way02(self):
        api = overpy.Overpass()
        # DOM
        result = api.parse_xml(read_file("xml/way-02.xml"), parser=overpy.XML_PARSER_DOM)
        self._test_way02(result)
        # SAX
        result = api.parse_xml(read_file("xml/way-02.xml"), parser=overpy.XML_PARSER_SAX)
        self._test_way02(result)

    def test_way03(self):
        api = overpy.Overpass()
        # DOM
        result = api.parse_xml(read_file("xml/way-03.xml"), parser=overpy.XML_PARSER_DOM)
        self._test_way03(result)
        # SAX
        result = api.parse_xml(read_file("xml/way-03.xml"), parser=overpy.XML_PARSER_SAX)
        self._test_way03(result)

    def test_way04(self):
        api = overpy.Overpass()
        # DOM
        with pytest.raises(ValueError):
            api.parse_xml(read_file("xml/way-04.xml"), parser=overpy.XML_PARSER_DOM)

        # SAX
        with pytest.raises(ValueError):
            api.parse_xml(read_file("xml/way-04.xml"), parser=overpy.XML_PARSER_SAX)


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
            overpy.RelationNode.from_xml(
                self._get_element_wrong_type()
            )

        with pytest.raises(overpy.exception.ElementDataWrongType):
            overpy.RelationWay.from_xml(
                self._get_element_wrong_type()
            )

        with pytest.raises(overpy.exception.ElementDataWrongType):
            overpy.Way.from_xml(
                self._get_element_wrong_type()
            )

    def test_node_missing_data(self):
        import xml.etree.ElementTree as ET

        # Tag without k attribute
        data = """<node id="1234"><tag></tag></node>"""
        node = ET.fromstring(data)
        with pytest.raises(ValueError):
            overpy.Node.from_xml(node)

    def test_relation_missing_data(self):
        import xml.etree.ElementTree as ET

        # Tag without k attribute
        data = """<relation id="1234"><tag></tag></relation>"""
        node = ET.fromstring(data)
        with pytest.raises(ValueError):
            overpy.Relation.from_xml(node)

    def test_way_missing_data(self):
        import xml.etree.ElementTree as ET

        # Node without ref attribute
        data = """<way id="1234"><nd></nd></way>"""
        node = ET.fromstring(data)
        with pytest.raises(ValueError):
            overpy.Way.from_xml(node)

        # Tag without k attribute
        data = """<way id="1234"><tag></tag></way>"""
        node = ET.fromstring(data)
        with pytest.raises(ValueError):
            overpy.Way.from_xml(node)
