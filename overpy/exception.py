class OverPyException(BaseException):
    """OverPy base exception"""
    pass


class OverpassBadRequest(OverPyException):
    """
    Raised if the Overpass API service returns a syntax error.

    :param query: The encoded query how it was send to the server
    :type query: Bytes
    :param msgs: List of error messages
    :type msgs: List
    """
    def __init__(self, query, msgs=None):
        self.query = query
        if msgs is None:
            msgs = []
        self.msgs = msgs

    def __str__(self):
        return "\n".join(self.msgs)


class OverpassTooManyRequests(OverPyException):
    """
    Raised if the Overpass API service returns a 429 status code.
    """
    def __init__(self):
        OverPyException.__init__(self, "Too many requests")


class OverpassUnknownContentType(OverPyException):
    """
    Raised if the reported content type isn't handled by OverPy.

    :param content_type: The reported content type
    :type content_type: None or String
    """
    def __init__(self, content_type):
        self.content_type = content_type

    def __str__(self):
        if self.content_type is None:
            return "No content type returned"
        return "Unknown content type: %s" % self.content_type


class OverpassUnknownHTTPStatusCode(OverPyException):
    """
    Raised if the returned HTTP status code isn't handled by OverPy.

    :param code: The HTTP status code
    :type code: Integer
    """
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return "Unknown/Unhandled status code: %d" % self.code