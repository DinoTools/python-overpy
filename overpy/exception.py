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