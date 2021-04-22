import pytest

import overpy
from overpy.format import geojson, osm_xml

from tests import read_file

from io import StringIO


class TestGeoJSON(object):
    def test_node01(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/node-01.json"))
        fp = StringIO()
        geojson.dump(result, fp, nodes=True, ways=True)


class TestOSMXML(object):
    def test_node01(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/node-01.json"))
        fp = StringIO()
        osm_xml.dump(result, fp)
