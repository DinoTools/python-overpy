import overpy


class TestExceptions(object):
    def test_element_data_wrong_type(self):
        e = overpy.exception.ElementDataWrongType("from1")
        assert e.type_expected == "from1"
        assert e.type_provided == None
        assert isinstance(str(e), str)

        e = overpy.exception.ElementDataWrongType("from2", "to2")
        assert e.type_expected == "from2"
        assert e.type_provided == "to2"
        assert isinstance(str(e), str)

    def test_overpass_bad_request(self):
        e = overpy.exception.OverpassBadRequest("query")
        assert e.query == "query"
        assert isinstance(e.msgs, list)
        assert len(e.msgs) == 0
        assert str(e) == ""

        e = overpy.exception.OverpassBadRequest("test\nquery\n123", ["abc", 1])
        assert e.query == "test\nquery\n123"
        assert isinstance(e.msgs, list)
        assert len(e.msgs) == 2
        assert str(e) == "abc\n1"

    def test_overpass_unknown_content_type(self):
        e = overpy.exception.OverpassUnknownContentType(None)
        assert e.content_type == None
        assert str(e).startswith("No content")

        e = overpy.exception.OverpassUnknownContentType("content")
        assert e.content_type == "content"
        assert str(e).startswith("Unknown content")
        assert str(e).endswith("content")

    def test_overpass_unknown_http_status_code(self):
        e = overpy.exception.OverpassUnknownHTTPStatusCode(123)
        assert e.code == 123
        assert str(e).endswith("123")