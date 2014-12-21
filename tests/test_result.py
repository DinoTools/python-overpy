import pytest

import overpy

from tests.base_class import read_file


class TestResult(object):
    def test_expand_error(self):
        api = overpy.Overpass()
        result = api.parse_json(read_file("json/result-expand-01.json"))
        with pytest.raises(ValueError):
            result.expand(123)
        with pytest.raises(ValueError):
            result.expand(1.23)
        with pytest.raises(ValueError):
            result.expand("abc")

    def test_expand_01(self):
        api = overpy.Overpass()
        result1 = api.parse_json(read_file("json/result-expand-01.json"))

        assert len(result1.nodes) == 2
        assert len(result1.ways) == 1

        result2 = api.parse_json(read_file("json/result-expand-02.json"))

        assert len(result2.nodes) == 2
        assert len(result2.ways) == 1

        result1.expand(result2)

        # Don't overwrite existing elements
        assert len(result1.nodes) == 3
        assert len(result1.ways) == 2