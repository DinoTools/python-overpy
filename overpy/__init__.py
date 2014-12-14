from decimal import Decimal
import json
import re
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY2:
    from urllib2 import urlopen
    from urllib2 import HTTPError
elif PY3:
    from urllib.request import urlopen
    from urllib.error import HTTPError


class Overpass(object):
    """
    Class to access the Overpass API
    """
    def __init__(self):
        self.url = "http://overpass-api.de/api/interpreter"
        self._regex_extract_error_msg = re.compile(b"\<p\>(?P<msg>\<strong\s.*?)\</p\>")
        self._regex_remove_tag = re.compile(b"<[^>]*?>")

    def query(self, query):
        """
        Query the Overpass API

        :param String|Bytes query: The query string in Overpass QL
        :return: The parsed result
        :rtype: overpy.Result
        """
        if not isinstance(query, bytes):
            query = bytes(query, "utf-8")
        try:
            f = urlopen(self.url, query)
        except HTTPError as e:
            msgs = []
            response = e.read(4096)
            while True:
                data = e.read(4096)
                if len(data) == 0:
                    break
                response = response + data

            for msg in self._regex_extract_error_msg.finditer(response):
                tmp = self._regex_remove_tag.sub(b"", msg.group("msg"))
                try:
                    tmp = tmp.decode("utf-8")
                except:
                    tmp = repr(tmp)
                msgs.append(tmp)

            raise Exception("\n".join(msgs))

        content_type = None
        if PY2:
            http_info = f.info()
            content_type = http_info.getheader("content-type")
        if PY3:
            content_type = f.getheader("Content-Type")

        response = f.read(4096)
        while True:
            data = f.read(4096)
            if len(data) == 0:
                break
            response = response + data

        f.close()

        if content_type == "application/json":
            return self.parse_json(response)

        # ToDo: Support XML
        # if content_type == "application/osm3s+xml":
        raise Exception

    def parse_json(self, data, encoding="utf-8"):
        """
        Parse raw response from Overpass service.

        :param data: Raw JSON Data
        :type data: String or Bytes
        :param encoding: Encoding to decode byte string
        :type encoding: String
        :return: Result object
        :rtype: overpy.Result
        """
        if isinstance(data, bytes):
            data = data.decode(encoding)
        data = json.loads(data, parse_float=Decimal)
        return Result.from_json(data, api=self)


class Result(object):
    """
    Class to handle the result.
    """
    def __init__(self, elements=None, api=None):
        """

        :param List elements:
        :param api:
        :type api: overpy.Overpass
        """
        if elements is None:
            elements = []
        self._elements = elements
        self.api = api

    def expand(self, other):
        """
        Add all elements from an other result to the list of elements of this result object.

        It is used by the auto resolve feature.

        :param other: Expand the result with the elements from this result.
        :type other: overpy.Result
        """
        if not isinstance(other, Result):
            raise Exception

        def do(ids, elements):
            for element in elements:
                if element.id is not None and element.id not in ids:
                    self._elements.append(element)
                    ids.append(element.id)

        do(self.node_ids, other.nodes)
        do(self.way_ids, other.ways)
        do(self.relation_ids, other.relations)

    def append(self, element):
        """
        Append a new element to the result.

        :param element: The element to append
        :type element: overpy.Element
        """
        self._elements.append(element)

    def get_elements(self, filter_cls, elem_id=None):
        """
        Get a list of elements from the result and filter the element type by a class.

        :param filter_cls:
        :param elem_id: ID of the object
        :type elem_id: Integer
        :return: List of available elements
        :rtype: List
        """
        result = []
        for e in self._elements:
            if not isinstance(e, filter_cls):
                continue
            if elem_id is not None and e.id != elem_id:
                continue
            result.append(e)
        return result

    def get_ids(self, filter_cls):
        """

        :param filter_cls:
        :return:
        """
        result = []
        for node in self.get_elements(filter_cls):
            if node.id is not None and node.id not in result:
                result.append(node.id)
        return result

    def get_node_ids(self):
        return self.get_ids(filter_cls=Node)

    def get_way_ids(self):
        return self.get_ids(filter_cls=Way)

    def get_relation_ids(self):
        return self.get_ids(filter_cls=Relation)

    node_ids = property(get_node_ids)
    relation_ids = property(get_relation_ids)
    way_ids = property(get_way_ids)

    @classmethod
    def from_json(cls, data, api=None):
        """
        Create a new instance and load data from json object.

        :param data: JSON data returned by the Overpass API
        :type data: Dict
        :param api:
        :type api: overpy.Overpass
        :return: New instance of Result object
        :rtype: overpy.Result
        """
        result = cls(api=api)
        for elem_cls in [Node, Way, Relation]:
            for element in data.get("elements", []):
                e_type = element.get("type")
                if hasattr(e_type, "lower") and e_type.lower() == elem_cls._type_value:
                    result.append(elem_cls.from_json(element, result=result))

        return result

    def get_node(self, node_id, resolve_missing=False):
        """
        Get a node by its ID.

        :param node_id: The node ID
        :type node_id: Integer
        :param resolve_missing: Query the Overpass API if the node is missing in the result set.
        :return: The node
        :rtype: overpy.Node
        """
        nodes = self.get_nodes(node_id=node_id)
        if len(nodes) == 0:
            if not resolve_missing:
                raise Exception

            query = ("\n"
                    "[out:json];\n"
                    "node({node_id});\n"
                    "out body;\n"
            )
            query = query.format(
                node_id=node_id
            )
            tmp_result = self.api.query(query)
            self.expand(tmp_result)

            nodes = self.get_nodes(node_id=node_id)

        if len(nodes) == 0:
            raise Exception

        return nodes[0]

    def get_nodes(self, node_id=None, **kwargs):
        """
        Alias for get_elements() but filter the result by Node()

        :param node_id: The Id of the node
        :type node_id: Integer
        :return: List of elements
        """
        return self.get_elements(Node, elem_id=node_id, **kwargs)

    def get_relation(self, rel_id, resolve_missing=False):
        """
        Get a relation by its ID.

        :param rel_id: The relation ID
        :type rel_id: Integer
        :param resolve_missing: Query the Overpass API if the relation is missing in the result set.
        :return: The relation
        :rtype: overpy.Relation
        """
        relations = self.get_relations(rel_id=rel_id)
        if len(relations) == 0:
            if resolve_missing is False:
                raise Exception

            query = ("\n"
                    "[out:json];\n"
                    "relation({relation_id});\n"
                    "out body;\n"
            )
            query = query.format(
                relation_id=rel_id
            )
            tmp_result = self.api.query(query)
            self.expand(tmp_result)

            relations = self.get_relations(rel_id=rel_id)

        if len(relations) == 0:
            raise Exception

        return relations[0]

    def get_relations(self, rel_id=None, **kwargs):
        """
        Alias for get_elements() but filter the result by Relation

        :param rel_id: Id of the relation
        :type rel_id: Integer
        :return: List of elements
        """
        return self.get_elements(Relation, elem_id=rel_id, **kwargs)

    def get_way(self, way_id, resolve_missing=False):
        """
        Get a way by its ID.

        :param way_id: The way ID
        :type way_id: Integer
        :param resolve_missing: Query the Overpass API if the way is missing in the result set.
        :return: The way
        :rtype: overpy.Way
        """
        ways = self.get_ways(way_id=way_id)
        if len(ways) == 0:
            if resolve_missing is False:
                raise Exception

            query = ("\n"
                    "[out:json];\n"
                    "way({way_id});\n"
                    "out body;\n"
            )
            query = query.format(
                way_id=way_id
            )
            tmp_result = self.api.query(query)
            self.expand(tmp_result)

            ways = self.get_ways(way_id=way_id)

        if len(ways) == 0:
            raise Exception

        return ways[0]

    def get_ways(self, way_id=None, **kwargs):
        """
        Alias for get_elements() but filter the result by Way

        :param way_id: The Id of the way
        :type way_id: Integer
        :return: List of elements
        """
        return self.get_elements(Way, elem_id=way_id, **kwargs)

    nodes = property(get_nodes)
    relations = property(get_relations)
    ways = property(get_ways)


class Element(object):
    """
    Base element
    """

    def __init__(self, attributes=None, result=None, tags=None):
        """
        :param attributes: Additional attributes
        :type attributes: Dict
        :param result: The result object this element belongs to
        :param tags: List of tags
        :type tags: Dict
        """

        self._result = result
        self.attributes = attributes
        self.tags = tags


class Node(Element):
    """
    Class to represent an element of type node
    """

    _type_value = "node"

    def __init__(self, node_id=None, lat=None, lon=None, **kwargs):
        """
        :param lat: Latitude
        :type lat: Decimal or Float
        :param lon: Longitude
        :type long: Decimal or Float
        :param node_id: Id of the node element
        :type node_id: Integer
        :param kwargs: Additional arguments are passed directly to the parent class
        """

        Element.__init__(self, **kwargs)
        self.id = node_id
        self.lat = lat
        self.lon = lon

    @classmethod
    def from_json(cls, data, result=None):
        if data.get("type") != cls._type_value:
            raise Exception

        tags = data.get("tags", {})

        node_id = data.get("id")
        lat = data.get("lat")
        lon = data.get("lon")

        attributes = {}
        ignore = ["type", "id", "lat", "lon", "tags"]
        for n, v in data.items():
            if n in ignore:
                continue
            attributes[n] = v

        return cls(node_id=node_id, lat=lat, lon=lon, tags=tags, attributes=attributes, result=result)


class Way(Element):
    """
    Class to represent an element of type way
    """

    _type_value = "way"

    def __init__(self, way_id=None, node_ids=None, **kwargs):
        """
        :param node_ids: List of node IDs
        :type node_ids: List or Tuple
        :param way_id: Id of the way element
        :type way_id: Integer
        :param kwargs: Additional arguments are passed directly to the parent class

        """

        Element.__init__(self, **kwargs)
        self.id = way_id
        self._node_ids = node_ids

    @property
    def nodes(self):
        return self.get_nodes()

    def get_nodes(self, resolve_missing=False):
        """
        Get the nodes defining the geometry of the way

        :param resolve_missing: Try to resolve missing nodes.
        :type resolve_missing: Boolean
        :return: List of nodes
        :rtype: List of overpy.Node
        """
        result = []
        resolved = False

        for node_id in self._node_ids:
            try:
                node = self._result.get_node(node_id)
            except:
                node = None
            if node is None:
                if resolved or not resolve_missing:
                    raise Exception

                query = ("\n"
                        "[out:json];\n"
                        "way({way_id});\n"
                        "node(w);\n"
                        "out body;\n"
                )
                query = query.format(
                    way_id=self.id
                )
                tmp_result = self._result.api.query(query)
                self._result.expand(tmp_result)
                resolved = True

                try:
                    node = self._result.get_node(node_id)
                except:
                    node = None

            if node is None:
                raise Exception

            result.append(node)

        return result

    @classmethod
    def from_json(cls, data, result=None):
        if data.get("type") != cls._type_value:
            raise Exception

        tags = data.get("tags", {})

        way_id = data.get("id")
        node_ids = data.get("nodes")

        attributes = {}
        ignore = ["id", "nodes", "tags", "type"]
        for n, v in data.items():
            if n in ignore:
                continue
            attributes[n] = v

        return cls(way_id=way_id, attributes=attributes, node_ids=node_ids, tags=tags, result=result)


class Relation(Element):
    """
    Class to represent an element of type relation
    """

    _type_value = "relation"

    def __init__(self, rel_id=None, members=None, **kwargs):
        """
        :param members:
        :param rel_id: Id of the relation element
        :type rel_id: Integer
        :param kwargs:
        :return:
        """

        Element.__init__(self, **kwargs)
        self.id = rel_id
        self.members = members

    @classmethod
    def from_json(cls, data, result=None):
        if data.get("type") != cls._type_value:
            raise Exception

        tags = data.get("tags", {})

        rel_id = data.get("id")

        members = []

        supported_members = [RelationNode, RelationWay]
        for member in data.get("members", []):
            type_value = member.get("type")
            for member_cls in supported_members:
                if member_cls._type_value == type_value:
                    members.append(
                        member_cls.from_json(
                            member,
                            result=result
                        )
                    )

        attributes = {}
        ignore = ["id", "members", "tags", "type"]
        for n, v in data.items():
            if n in ignore:
                continue
            attributes[n] = v

        return cls(rel_id=rel_id, attributes=attributes, members=members, tags=tags, result=result)


class RelationMember(object):
    """
    Base class to represent a member of a relation.
    """
    def __init__(self, ref=None, role=None, result=None):
        """
        :param ref: Reference Id
        :type ref: Integer
        :param role: The role of the relation member
        :type role: String
        :param result:
        """
        self.ref = ref
        self._result = result
        self.role = role

    @classmethod
    def from_json(cls, data, result=None):
        if data.get("type") != cls._type_value:
            raise Exception

        ref = data.get("ref")
        role = data.get("role")
        return cls(ref=ref, role=role, result=result)


class RelationNode(RelationMember):
    _type_value = "node"

    def resolve(self, resolve_missing=False):
        return self._result.get_node(self.ref, resolve_missing=resolve_missing)


class RelationWay(RelationMember):
    _type_value = "way"

    def resolve(self, resolve_missing=False):
        return self._result.get_way(self.ref, resolve_missing=resolve_missing)
