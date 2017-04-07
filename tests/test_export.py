import pytest

import overpy
from overpy import PY2
from overpy.format import geojson

from tests.base_class import read_file

if PY2:
    from StringIO import StringIO
else:
    from io import StringIO


class TestGeoJSON(object):
    def test_node01(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/node-01.json"))
        fp = StringIO()
        geojson.dump(result, fp, nodes=True, ways=True)
