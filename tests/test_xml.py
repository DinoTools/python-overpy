from decimal import Decimal
import os

import overpy

from base_class import BaseTestNodes, BaseTestWay


def read_file(filename):
    filename = os.path.join(os.path.dirname(__file__), filename)
    return open(filename).read()


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