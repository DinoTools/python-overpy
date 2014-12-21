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