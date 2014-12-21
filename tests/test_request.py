import pytest

import overpy


class TestQuery(object):
    def test_syntax_error(self):
        with pytest.raises(overpy.exception.OverpassBadRequest):
            api = overpy.Overpass()
            # Missing ; after way(1)
            api.query((
                "way(1)"
                "out body;"
            ))

    def test_json_response(self):
        api = overpy.Overpass()
        result = api.query("[out:json];node(50.745,7.17,50.75,7.18);out;")
        assert len(result.nodes) > 0

    def test_xml_response(self):
        api = overpy.Overpass()
        result = api.query("[out:xml];node(50.745,7.17,50.75,7.18);out;")
        assert len(result.nodes) > 0