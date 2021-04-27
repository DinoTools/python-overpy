from collections import OrderedDict
from datetime import datetime
from decimal import Decimal
from urllib.request import urlopen
from urllib.error import HTTPError
from xml.sax import handler, make_parser
import xml.etree.ElementTree
import json
import re
import time
from typing import Any, Callable, ClassVar, Dict, List, NoReturn, Optional, Tuple, Type, TypeVar, Union

from overpy import exception
# Ignore flake8 F401 warning for unused vars
from overpy.__about__ import (  # noqa: F401
    __author__, __copyright__, __email__, __license__, __summary__, __title__,
    __uri__, __version__
)

ElementTypeVar = TypeVar("ElementTypeVar", bound="Element")

XML_PARSER_DOM = 1
XML_PARSER_SAX = 2

# Try to convert some common attributes
# http://wiki.openstreetmap.org/wiki/Elements#Common_attributes
GLOBAL_ATTRIBUTE_MODIFIERS: Dict[str, Callable] = {
    "changeset": int,
    "timestamp": lambda ts: datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"),
    "uid": int,
    "version": int,
    "visible": lambda v: v.lower() == "true"
}


def is_valid_type(
        element: Union["Area", "Node", "Relation", "Way"],
        cls: Type[Union["Area", "Element", "Node", "Relation", "Way"]]) -> bool:
    """
    Test if an element is of a given type.

    :param element: The element instance to test
    :param cls: The element class to test
    :return: False or True
    """
    return isinstance(element, cls) and element.id is not None


class Overpass:
    """
    Class to access the Overpass API

    :cvar default_max_retry_count: Global max number of retries (Default: 0)
    :cvar default_read_chunk_size: Max size of each chunk read from the server response
    :cvar default_retry_timeout: Global time to wait between tries (Default: 1.0s)
    :cvar default_url: Default URL of the Overpass server
    """
    default_max_retry_count: ClassVar[int] = 0
    default_read_chunk_size: ClassVar[int] = 4096
    default_retry_timeout: ClassVar[float] = 1.0
    default_url: ClassVar[str] = "http://overpass-api.de/api/interpreter"

    def __init__(
            self,
            read_chunk_size: Optional[int] = None,
            url: Optional[str] = None,
            xml_parser: int = XML_PARSER_SAX,
            max_retry_count: int = None,
            retry_timeout: float = None):
        """
        :param read_chunk_size: Max size of each chunk read from the server response
        :param url: Optional URL of the Overpass server. Defaults to http://overpass-api.de/api/interpreter
        :param xml_parser: The xml parser to use
        :param max_retry_count: Max number of retries (Default: default_max_retry_count)
        :param retry_timeout: Time to wait between tries (Default: default_retry_timeout)
        """
        self.url = self.default_url
        if url is not None:
            self.url = url

        self._regex_extract_error_msg = re.compile(br"\<p\>(?P<msg>\<strong\s.*?)\</p\>")
        self._regex_remove_tag = re.compile(b"<[^>]*?>")
        if read_chunk_size is None:
            read_chunk_size = self.default_read_chunk_size
        self.read_chunk_size = read_chunk_size

        if max_retry_count is None:
            max_retry_count = self.default_max_retry_count
        self.max_retry_count = max_retry_count

        if retry_timeout is None:
            retry_timeout = self.default_retry_timeout
        self.retry_timeout = retry_timeout

        self.xml_parser = xml_parser

    @staticmethod
    def _handle_remark_msg(msg: str) -> NoReturn:
        """
        Try to parse the message provided with the remark tag or element.

        :param msg: The message
        :raises overpy.exception.OverpassRuntimeError: If message starts with 'runtime error:'
        :raises overpy.exception.OverpassRuntimeRemark: If message starts with 'runtime remark:'
        :raises overpy.exception.OverpassUnknownError: If we are unable to identify the error
        """
        msg = msg.strip()
        if msg.startswith("runtime error:"):
            raise exception.OverpassRuntimeError(msg=msg)
        elif msg.startswith("runtime remark:"):
            raise exception.OverpassRuntimeRemark(msg=msg)
        raise exception.OverpassUnknownError(msg=msg)

    def query(self, query: Union[bytes, str]) -> "Result":
        """
        Query the Overpass API

        :param query: The query string in Overpass QL
        :return: The parsed result
        """
        if not isinstance(query, bytes):
            query = query.encode("utf-8")

        retry_num: int = 0
        retry_exceptions: List[exception.OverPyException] = []
        do_retry: bool = True if self.max_retry_count > 0 else False
        while retry_num <= self.max_retry_count:
            if retry_num > 0:
                time.sleep(self.retry_timeout)
            retry_num += 1
            try:
                f = urlopen(self.url, query)
            except HTTPError as e:
                f = e

            response = f.read(self.read_chunk_size)
            while True:
                data = f.read(self.read_chunk_size)
                if len(data) == 0:
                    break
                response = response + data
            f.close()

            current_exception: exception.OverPyException
            if f.code == 200:
                content_type = f.getheader("Content-Type")

                if content_type == "application/json":
                    return self.parse_json(response)

                if content_type == "application/osm3s+xml":
                    return self.parse_xml(response)

                current_exception = exception.OverpassUnknownContentType(content_type)
                if not do_retry:
                    raise current_exception
                retry_exceptions.append(current_exception)
                continue

            if f.code == 400:
                msgs: List[str] = []
                for msg_raw in self._regex_extract_error_msg.finditer(response):
                    msg_clean_bytes = self._regex_remove_tag.sub(b"", msg_raw.group("msg"))
                    try:
                        msg = msg_clean_bytes.decode("utf-8")
                    except UnicodeDecodeError:
                        msg = repr(msg_clean_bytes)
                    msgs.append(msg)

                current_exception = exception.OverpassBadRequest(
                    query,
                    msgs=msgs
                )
                if not do_retry:
                    raise current_exception
                retry_exceptions.append(current_exception)
                continue

            if f.code == 429:
                current_exception = exception.OverpassTooManyRequests()
                if not do_retry:
                    raise current_exception
                retry_exceptions.append(current_exception)
                continue

            if f.code == 504:
                current_exception = exception.OverpassGatewayTimeout()
                if not do_retry:
                    raise current_exception
                retry_exceptions.append(current_exception)
                continue

            current_exception = exception.OverpassUnknownHTTPStatusCode(f.code)
            if not do_retry:
                raise current_exception
            retry_exceptions.append(current_exception)
            continue

        raise exception.MaxRetriesReached(retry_count=retry_num, exceptions=retry_exceptions)

    def parse_json(self, data: Union[bytes, str], encoding: str = "utf-8") -> "Result":
        """
        Parse raw response from Overpass service.

        :param data: Raw JSON Data
        :param encoding: Encoding to decode byte string
        :return: Result object
        """
        if isinstance(data, bytes):
            data = data.decode(encoding)
        data_parsed: dict = json.loads(data, parse_float=Decimal)
        if "remark" in data_parsed:
            self._handle_remark_msg(msg=data_parsed.get("remark"))
        return Result.from_json(data_parsed, api=self)

    def parse_xml(self, data: Union[bytes, str], encoding: str = "utf-8", parser: Optional[int] = None):
        """

        :param data: Raw XML Data
        :param encoding: Encoding to decode byte string
        :param parser: The XML parser to use
        :return: Result object
        """
        if parser is None:
            parser = self.xml_parser

        if isinstance(data, bytes):
            data = data.decode(encoding)

        m = re.compile("<remark>(?P<msg>[^<>]*)</remark>").search(data)
        if m:
            self._handle_remark_msg(m.group("msg"))

        return Result.from_xml(data, api=self, parser=parser)


class Result:
    """
    Class to handle the result.
    """

    def __init__(
            self,
            elements: Optional[List[Union["Area", "Node", "Relation", "Way"]]] = None,
            api: Optional[Overpass] = None):
        """

        :param elements: List of elements to initialize the result with
        :param api: The API object to load additional resources and elements
        """
        if elements is None:
            elements = []
        self._areas: Dict[int, Union["Area", "Node", "Relation", "Way"]] = OrderedDict(
            (element.id, element) for element in elements if is_valid_type(element, Area)
        )
        self._nodes = OrderedDict(
            (element.id, element) for element in elements if is_valid_type(element, Node)
        )
        self._ways = OrderedDict(
            (element.id, element) for element in elements if is_valid_type(element, Way)
        )
        self._relations = OrderedDict(
            (element.id, element) for element in elements if is_valid_type(element, Relation)
        )
        self._class_collection_map: Dict[Any, Any] = {
            Node: self._nodes,
            Way: self._ways,
            Relation: self._relations,
            Area: self._areas
        }
        self.api = api

    def expand(self, other: "Result"):
        """
        Add all elements from an other result to the list of elements of this result object.

        It is used by the auto resolve feature.

        :param other: Expand the result with the elements from this result.
        :raises ValueError: If provided parameter is not instance of :class:`overpy.Result`
        """
        if not isinstance(other, Result):
            raise ValueError("Provided argument has to be instance of overpy:Result()")

        other_collection_map: Dict[Type["Element"], List[Union["Area", "Node", "Relation", "Way"]]] = {
            Area: other.areas,
            Node: other.nodes,
            Relation: other.relations,
            Way: other.ways
        }
        for element_type, own_collection in self._class_collection_map.items():
            for element in other_collection_map[element_type]:
                if is_valid_type(element, element_type) and element.id not in own_collection:
                    own_collection[element.id] = element

    def append(self, element: Union["Area", "Node", "Relation", "Way"]):
        """
        Append a new element to the result.

        :param element: The element to append
        """
        if is_valid_type(element, Element):
            self._class_collection_map[element.__class__].setdefault(element.id, element)

    def get_elements(
            self,
            filter_cls: Type[ElementTypeVar],
            elem_id: Optional[int] = None) -> List[ElementTypeVar]:
        """
        Get a list of elements from the result and filter the element type by a class.

        :param filter_cls:
        :param elem_id: ID of the object
        :return: List of available elements
        """
        result: List[ElementTypeVar] = []
        if elem_id is not None:
            try:
                result = [self._class_collection_map[filter_cls][elem_id]]
            except KeyError:
                result = []
        else:
            for e in self._class_collection_map[filter_cls].values():
                result.append(e)
        return result

    def get_ids(
            self,
            filter_cls: Type[Union["Area", "Node", "Relation", "Way"]]) -> List[int]:
        """
        Get all Element IDs

        :param filter_cls: Only IDs of elements with this type
        :return: List of IDs
        """
        return list(self._class_collection_map[filter_cls].keys())

    def get_node_ids(self) -> List[int]:
        return self.get_ids(filter_cls=Node)

    def get_way_ids(self) -> List[int]:
        return self.get_ids(filter_cls=Way)

    def get_relation_ids(self) -> List[int]:
        return self.get_ids(filter_cls=Relation)

    def get_area_ids(self) -> List[int]:
        return self.get_ids(filter_cls=Area)

    @classmethod
    def from_json(cls, data: dict, api: Optional[Overpass] = None) -> "Result":
        """
        Create a new instance and load data from json object.

        :param data: JSON data returned by the Overpass API
        :param api:
        :return: New instance of Result object
        """
        result = cls(api=api)
        elem_cls: Type[Union["Area", "Node", "Relation", "Way"]]
        for elem_cls in [Node, Way, Relation, Area]:
            for element in data.get("elements", []):
                e_type = element.get("type")
                if hasattr(e_type, "lower") and e_type.lower() == elem_cls._type_value:
                    result.append(elem_cls.from_json(element, result=result))

        return result

    @classmethod
    def from_xml(
            cls,
            data: Union[str, xml.etree.ElementTree.Element],
            api: Optional[Overpass] = None,
            parser: Optional[int] = None) -> "Result":
        """
        Create a new instance and load data from xml data or object.

        .. note::
            If parser is set to None, the functions tries to find the best parse.
            By default the SAX parser is chosen if a string is provided as data.
            The parser is set to DOM if an xml.etree.ElementTree.Element is provided as data value.

        :param data: Root element
        :param api: The instance to query additional information if required.
        :param parser: Specify the parser to use(DOM or SAX)(Default: None = autodetect, defaults to SAX)
        :return: New instance of Result object
        """
        if parser is None:
            if isinstance(data, str):
                parser = XML_PARSER_SAX
            else:
                parser = XML_PARSER_DOM

        result = cls(api=api)
        if parser == XML_PARSER_DOM:
            import xml.etree.ElementTree as ET
            if isinstance(data, str):
                root = ET.fromstring(data)
            elif isinstance(data, ET.Element):
                root = data
            else:
                raise exception.OverPyException("Unable to detect data type.")

            elem_cls: Type[Union["Area", "Node", "Relation", "Way"]]
            for elem_cls in [Node, Way, Relation, Area]:
                for child in root:
                    if child.tag.lower() == elem_cls._type_value:
                        result.append(elem_cls.from_xml(child, result=result))

        elif parser == XML_PARSER_SAX:
            from io import StringIO
            if not isinstance(data, str):
                raise ValueError("data must be of type str if using the SAX parser")
            source = StringIO(data)
            sax_handler = OSMSAXHandler(result)
            sax_parser = make_parser()
            sax_parser.setContentHandler(sax_handler)
            sax_parser.parse(source)
        else:
            # ToDo: better exception
            raise Exception("Unknown XML parser")
        return result

    def get_area(self, area_id: int, resolve_missing: bool = False) -> "Area":
        """
        Get an area by its ID.

        :param area_id: The area ID
        :param resolve_missing: Query the Overpass API if the area is missing in the result set.
        :return: The area
        :raises overpy.exception.DataIncomplete: The requested way is not available in the result cache.
        :raises overpy.exception.DataIncomplete: If resolve_missing is True and the area can't be resolved.
        """
        areas = self.get_areas(area_id=area_id)
        if len(areas) == 0:
            if resolve_missing is False:
                raise exception.DataIncomplete("Resolve missing area is disabled")

            query = ("\n"
                     "[out:json];\n"
                     "area({area_id});\n"
                     "out body;\n"
                     )
            query = query.format(
                area_id=area_id
            )
            tmp_result = self.api.query(query)
            self.expand(tmp_result)

            areas = self.get_areas(area_id=area_id)

        if len(areas) == 0:
            raise exception.DataIncomplete("Unable to resolve requested areas")

        return areas[0]

    def get_areas(self, area_id: Optional[int] = None) -> List["Area"]:
        """
        Alias for get_elements() but filter the result by Area

        :param area_id: The Id of the area
        :return: List of elements
        """
        return self.get_elements(Area, elem_id=area_id)

    def get_node(self, node_id: int, resolve_missing: bool = False) -> "Node":
        """
        Get a node by its ID.

        :param node_id: The node ID
        :param resolve_missing: Query the Overpass API if the node is missing in the result set.
        :return: The node
        :raises overpy.exception.DataIncomplete: At least one referenced node is not available in the result cache.
        :raises overpy.exception.DataIncomplete: If resolve_missing is True and at least one node can't be resolved.
        """
        nodes = self.get_nodes(node_id=node_id)
        if len(nodes) == 0:
            if not resolve_missing:
                raise exception.DataIncomplete("Resolve missing nodes is disabled")

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
            raise exception.DataIncomplete("Unable to resolve all nodes")

        return nodes[0]

    def get_nodes(self, node_id: Optional[int] = None) -> List["Node"]:
        """
        Alias for get_elements() but filter the result by Node()

        :param node_id: The Id of the node
        :type node_id: Integer
        :return: List of elements
        """
        return self.get_elements(Node, elem_id=node_id)

    def get_relation(self, rel_id: int, resolve_missing: bool = False) -> "Relation":
        """
        Get a relation by its ID.

        :param rel_id: The relation ID
        :param resolve_missing: Query the Overpass API if the relation is missing in the result set.
        :return: The relation
        :raises overpy.exception.DataIncomplete: The requested relation is not available in the result cache.
        :raises overpy.exception.DataIncomplete: If resolve_missing is True and the relation can't be resolved.
        """
        relations = self.get_relations(rel_id=rel_id)
        if len(relations) == 0:
            if resolve_missing is False:
                raise exception.DataIncomplete("Resolve missing relations is disabled")

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
            raise exception.DataIncomplete("Unable to resolve requested reference")

        return relations[0]

    def get_relations(self, rel_id: int = None) -> List["Relation"]:
        """
        Alias for get_elements() but filter the result by Relation

        :param rel_id: Id of the relation
        :return: List of elements
        """
        return self.get_elements(Relation, elem_id=rel_id)

    def get_way(self, way_id: int, resolve_missing: bool = False) -> "Way":
        """
        Get a way by its ID.

        :param way_id: The way ID
        :param resolve_missing: Query the Overpass API if the way is missing in the result set.
        :return: The way
        :raises overpy.exception.DataIncomplete: The requested way is not available in the result cache.
        :raises overpy.exception.DataIncomplete: If resolve_missing is True and the way can't be resolved.
        """
        ways = self.get_ways(way_id=way_id)
        if len(ways) == 0:
            if resolve_missing is False:
                raise exception.DataIncomplete("Resolve missing way is disabled")

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
            raise exception.DataIncomplete("Unable to resolve requested way")

        return ways[0]

    def get_ways(self, way_id: Optional[int] = None) -> List["Way"]:
        """
        Alias for get_elements() but filter the result by Way

        :param way_id: The Id of the way
        :return: List of elements
        """
        return self.get_elements(Way, elem_id=way_id)

    area_ids = property(get_area_ids)
    areas = property(get_areas)
    node_ids = property(get_node_ids)
    nodes = property(get_nodes)
    relation_ids = property(get_relation_ids)
    relations = property(get_relations)
    way_ids = property(get_way_ids)
    ways = property(get_ways)


class Element:
    """
    Base element
    """

    _type_value: str

    def __init__(self, attributes: Optional[dict] = None, result: Optional[Result] = None, tags: Optional[Dict] = None):
        """
        :param attributes: Additional attributes
        :param result: The result object this element belongs to
        :param tags: List of tags
        """

        self._result = result
        self.attributes = attributes
        # ToDo: Add option to modify attribute modifiers
        attribute_modifiers: Dict[str, Callable] = dict(GLOBAL_ATTRIBUTE_MODIFIERS.items())
        for n, m in attribute_modifiers.items():
            if n in self.attributes:
                self.attributes[n] = m(self.attributes[n])
        self.id: int
        self.tags = tags

    @classmethod
    def get_center_from_json(cls, data: dict) -> Tuple[Decimal, Decimal]:
        """
        Get center information from json data

        :param data: json data
        :return: tuple with two elements: lat and lon
        """
        center_lat = None
        center_lon = None
        center = data.get("center")
        if isinstance(center, dict):
            center_lat = center.get("lat")
            center_lon = center.get("lon")
            if center_lat is None or center_lon is None:
                raise ValueError("Unable to get lat or lon of way center.")
            center_lat = Decimal(center_lat)
            center_lon = Decimal(center_lon)
        return center_lat, center_lon

    @classmethod
    def get_center_from_xml_dom(cls, sub_child: xml.etree.ElementTree.Element) -> Tuple[Decimal, Decimal]:
        center_lat_str: str = sub_child.attrib.get("lat")
        center_lon_str: str = sub_child.attrib.get("lon")
        if center_lat_str is None or center_lon_str is None:
            raise ValueError("Unable to get lat or lon of way center.")
        center_lat = Decimal(center_lat_str)
        center_lon = Decimal(center_lon_str)
        return center_lat, center_lon

    @classmethod
    def from_json(cls: Type[ElementTypeVar], data: dict, result: Optional[Result] = None) -> ElementTypeVar:
        """
        Create new Element() from json data
        :param data:
        :param result:
        :return:
        """
        raise NotImplementedError

    @classmethod
    def from_xml(
            cls: Type[ElementTypeVar],
            child: xml.etree.ElementTree.Element,
            result: Optional[Result] = None) -> ElementTypeVar:
        """
        Create new Element() element from XML data
        """
        raise NotImplementedError


class Area(Element):
    """
    Class to represent an element of type area
    """

    _type_value = "area"

    def __init__(self, area_id: Optional[int] = None, **kwargs):
        """
        :param area_id: Id of the area element
        :param kwargs: Additional arguments are passed directly to the parent class
        """

        Element.__init__(self, **kwargs)
        #: The id of the way
        self.id = area_id

    def __repr__(self) -> str:
        return f"<overpy.Area id={self.id}>"

    @classmethod
    def from_json(cls, data: dict, result: Optional[Result] = None) -> "Area":
        """
        Create new Area element from JSON data

        :param data: Element data from JSON
        :param result: The result this element belongs to
        :return: New instance of Way
        :raises overpy.exception.ElementDataWrongType: If type value of the passed JSON data does not match.
        """
        if data.get("type") != cls._type_value:
            raise exception.ElementDataWrongType(
                type_expected=cls._type_value,
                type_provided=data.get("type")
            )

        tags = data.get("tags", {})

        area_id = data.get("id")

        attributes = {}
        ignore = ["id", "tags", "type"]
        for n, v in data.items():
            if n in ignore:
                continue
            attributes[n] = v

        return cls(area_id=area_id, attributes=attributes, tags=tags, result=result)

    @classmethod
    def from_xml(cls, child: xml.etree.ElementTree.Element, result: Optional[Result] = None) -> "Area":
        """
        Create new way element from XML data

        :param child: XML node to be parsed
        :param result: The result this node belongs to
        :return: New Way oject
        :raises overpy.exception.ElementDataWrongType: If name of the xml child node doesn't match
        :raises ValueError: If the ref attribute of the xml node is not provided
        :raises ValueError: If a tag doesn't have a name
        """
        if child.tag.lower() != cls._type_value:
            raise exception.ElementDataWrongType(
                type_expected=cls._type_value,
                type_provided=child.tag.lower()
            )

        tags = {}

        for sub_child in child:
            if sub_child.tag.lower() == "tag":
                name = sub_child.attrib.get("k")
                if name is None:
                    raise ValueError("Tag without name/key.")
                value = sub_child.attrib.get("v")
                tags[name] = value

        area_id_str: Optional[str] = child.attrib.get("id")
        area_id: Optional[int] = None
        if area_id_str is not None:
            area_id = int(area_id_str)

        attributes = {}
        ignore = ["id"]
        for n, v in child.attrib.items():
            if n in ignore:
                continue
            attributes[n] = v

        return cls(area_id=area_id, attributes=attributes, tags=tags, result=result)


class Node(Element):
    """
    Class to represent an element of type node
    """

    _type_value = "node"

    def __init__(
            self,
            node_id: Optional[int] = None,
            lat: Optional[Union[Decimal, float]] = None,
            lon: Optional[Union[Decimal, float]] = None,
            **kwargs):
        """
        :param lat: Latitude
        :param lon: Longitude
        :param node_id: Id of the node element
        :param kwargs: Additional arguments are passed directly to the parent class
        """

        Element.__init__(self, **kwargs)
        self.id = node_id
        self.lat = lat
        self.lon = lon

    def __repr__(self) -> str:
        return f"<overpy.Node id={self.id} lat={self.lat} lon={self.lon}>"

    @classmethod
    def from_json(cls, data: dict, result: Optional[Result] = None) -> "Node":
        """
        Create new Node element from JSON data

        :param data: Element data from JSON
        :param result: The result this element belongs to
        :return: New instance of Node
        :raises overpy.exception.ElementDataWrongType: If type value of the passed JSON data does not match.
        """
        if data.get("type") != cls._type_value:
            raise exception.ElementDataWrongType(
                type_expected=cls._type_value,
                type_provided=data.get("type")
            )

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

    @classmethod
    def from_xml(cls, child: xml.etree.ElementTree.Element, result: Optional[Result] = None) -> "Node":
        """
        Create new way element from XML data

        :param child: XML node to be parsed
        :param result: The result this node belongs to
        :return: New Way oject
        :raises overpy.exception.ElementDataWrongType: If name of the xml child node doesn't match
        :raises ValueError: If a tag doesn't have a name
        """
        if child.tag.lower() != cls._type_value:
            raise exception.ElementDataWrongType(
                type_expected=cls._type_value,
                type_provided=child.tag.lower()
            )

        tags = {}

        for sub_child in child:
            if sub_child.tag.lower() == "tag":
                name = sub_child.attrib.get("k")
                if name is None:
                    raise ValueError("Tag without name/key.")
                value = sub_child.attrib.get("v")
                tags[name] = value

        node_id: Optional[int] = None
        node_id_str: Optional[str] = child.attrib.get("id")
        if node_id_str is not None:
            node_id = int(node_id_str)

        lat: Optional[Decimal] = None
        lat_str: Optional[str] = child.attrib.get("lat")
        if lat_str is not None:
            lat = Decimal(lat_str)

        lon: Optional[Decimal] = None
        lon_str: Optional[str] = child.attrib.get("lon")
        if lon_str is not None:
            lon = Decimal(lon_str)

        attributes = {}
        ignore = ["id", "lat", "lon"]
        for n, v in child.attrib.items():
            if n in ignore:
                continue
            attributes[n] = v

        return cls(node_id=node_id, lat=lat, lon=lon, tags=tags, attributes=attributes, result=result)


class Way(Element):
    """
    Class to represent an element of type way
    """

    _type_value = "way"

    def __init__(
            self,
            way_id: Optional[int] = None,
            center_lat: Optional[Union[Decimal, float]] = None,
            center_lon: Optional[Union[Decimal, float]] = None,
            node_ids: Optional[Union[List[int], Tuple[int]]] = None,
            **kwargs):
        """
        :param node_ids: List of node IDs
        :param way_id: Id of the way element
        :param kwargs: Additional arguments are passed directly to the parent class
        """

        Element.__init__(self, **kwargs)
        #: The id of the way
        self.id = way_id

        #: List of Ids of the associated nodes
        self._node_ids = node_ids

        #: The lat/lon of the center of the way (optional depending on query)
        self.center_lat = center_lat
        self.center_lon = center_lon

    def __repr__(self):
        return f"<overpy.Way id={self.id} nodes={self._node_ids}>"

    @property
    def nodes(self) -> List[Node]:
        """
        List of nodes associated with the way.
        """
        return self.get_nodes()

    def get_nodes(self, resolve_missing: bool = False) -> List[Node]:
        """
        Get the nodes defining the geometry of the way

        :param resolve_missing: Try to resolve missing nodes.
        :return: List of nodes
        :raises overpy.exception.DataIncomplete: At least one referenced node is not available in the result cache.
        :raises overpy.exception.DataIncomplete: If resolve_missing is True and at least one node can't be resolved.
        """
        result = []
        resolved = False

        for node_id in self._node_ids:
            try:
                node = self._result.get_node(node_id)
            except exception.DataIncomplete:
                node = None

            if node is not None:
                result.append(node)
                continue

            if not resolve_missing:
                raise exception.DataIncomplete("Resolve missing nodes is disabled")

            # We tried to resolve the data but some nodes are still missing
            if resolved:
                raise exception.DataIncomplete("Unable to resolve all nodes")

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
            except exception.DataIncomplete:
                node = None

            if node is None:
                raise exception.DataIncomplete("Unable to resolve all nodes")

            result.append(node)

        return result

    @classmethod
    def from_json(cls, data: dict, result: Optional[Result] = None) -> "Way":
        """
        Create new Way element from JSON data

        :param data: Element data from JSON
        :param result: The result this element belongs to
        :return: New instance of Way
        :raises overpy.exception.ElementDataWrongType: If type value of the passed JSON data does not match.
        """
        if data.get("type") != cls._type_value:
            raise exception.ElementDataWrongType(
                type_expected=cls._type_value,
                type_provided=data.get("type")
            )

        tags = data.get("tags", {})

        way_id = data.get("id")
        node_ids = data.get("nodes")
        (center_lat, center_lon) = cls.get_center_from_json(data=data)

        attributes = {}
        ignore = ["center", "id", "nodes", "tags", "type"]
        for n, v in data.items():
            if n in ignore:
                continue
            attributes[n] = v

        return cls(
            attributes=attributes,
            center_lat=center_lat,
            center_lon=center_lon,
            node_ids=node_ids,
            tags=tags,
            result=result,
            way_id=way_id
        )

    @classmethod
    def from_xml(cls, child: xml.etree.ElementTree.Element, result: Optional[Result] = None) -> "Way":
        """
        Create new way element from XML data

        :param child: XML node to be parsed
        :param result: The result this node belongs to
        :return: New Way oject
        :raises overpy.exception.ElementDataWrongType: If name of the xml child node doesn't match
        :raises ValueError: If the ref attribute of the xml node is not provided
        :raises ValueError: If a tag doesn't have a name
        """
        if child.tag.lower() != cls._type_value:
            raise exception.ElementDataWrongType(
                type_expected=cls._type_value,
                type_provided=child.tag.lower()
            )

        tags = {}
        node_ids = []
        center_lat = None
        center_lon = None

        for sub_child in child:
            if sub_child.tag.lower() == "tag":
                name = sub_child.attrib.get("k")
                if name is None:
                    raise ValueError("Tag without name/key.")
                value = sub_child.attrib.get("v")
                tags[name] = value
            if sub_child.tag.lower() == "nd":
                ref_id_str = sub_child.attrib.get("ref")
                if ref_id_str is None:
                    raise ValueError("Unable to find required ref value.")
                ref_id: int = int(ref_id_str)
                node_ids.append(ref_id)
            if sub_child.tag.lower() == "center":
                (center_lat, center_lon) = cls.get_center_from_xml_dom(sub_child=sub_child)

        way_id: Optional[int] = None
        way_id_str: Optional[str] = child.attrib.get("id")
        if way_id_str is not None:
            way_id = int(way_id_str)

        attributes = {}
        ignore = ["id"]
        for n, v in child.attrib.items():
            if n in ignore:
                continue
            attributes[n] = v

        return cls(way_id=way_id, center_lat=center_lat, center_lon=center_lon,
                   attributes=attributes, node_ids=node_ids, tags=tags, result=result)


class Relation(Element):
    """
    Class to represent an element of type relation
    """

    _type_value = "relation"

    def __init__(
            self,
            rel_id: Optional[int] = None,
            center_lat: Optional[Union[Decimal, float]] = None,
            center_lon: Optional[Union[Decimal, float]] = None,
            members: Optional[List["RelationMember"]] = None,
            **kwargs):
        """
        :param members:
        :param rel_id: Id of the relation element
        :param kwargs:
        :return:
        """

        Element.__init__(self, **kwargs)
        self.id = rel_id
        self.members = members

        #: The lat/lon of the center of the way (optional depending on query)
        self.center_lat = center_lat
        self.center_lon = center_lon

    def __repr__(self):
        return f"<overpy.Relation id={self.id}>"

    @classmethod
    def from_json(cls, data: dict, result: Optional[Result] = None) -> "Relation":
        """
        Create new Relation element from JSON data

        :param data: Element data from JSON
        :param result: The result this element belongs to
        :return: New instance of Relation
        :raises overpy.exception.ElementDataWrongType: If type value of the passed JSON data does not match.
        """
        if data.get("type") != cls._type_value:
            raise exception.ElementDataWrongType(
                type_expected=cls._type_value,
                type_provided=data.get("type")
            )

        tags = data.get("tags", {})

        rel_id = data.get("id")
        (center_lat, center_lon) = cls.get_center_from_json(data=data)

        members = []

        supported_members = [RelationNode, RelationWay, RelationRelation]
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

        return cls(
            rel_id=rel_id,
            attributes=attributes,
            center_lat=center_lat,
            center_lon=center_lon,
            members=members,
            tags=tags,
            result=result
        )

    @classmethod
    def from_xml(cls, child: xml.etree.ElementTree.Element, result: Optional[Result] = None) -> "Relation":
        """
        Create new way element from XML data

        :param child: XML node to be parsed
        :param result: The result this node belongs to
        :return: New Way oject
        :raises overpy.exception.ElementDataWrongType: If name of the xml child node doesn't match
        :raises ValueError: If a tag doesn't have a name
        """
        if child.tag.lower() != cls._type_value:
            raise exception.ElementDataWrongType(
                type_expected=cls._type_value,
                type_provided=child.tag.lower()
            )

        tags = {}
        members = []
        center_lat = None
        center_lon = None

        supported_members = [RelationNode, RelationWay, RelationRelation, RelationArea]
        for sub_child in child:
            if sub_child.tag.lower() == "tag":
                name = sub_child.attrib.get("k")
                if name is None:
                    raise ValueError("Tag without name/key.")
                value = sub_child.attrib.get("v")
                tags[name] = value
            if sub_child.tag.lower() == "member":
                type_value = sub_child.attrib.get("type")
                for member_cls in supported_members:
                    if member_cls._type_value == type_value:
                        members.append(
                            member_cls.from_xml(
                                sub_child,
                                result=result
                            )
                        )
            if sub_child.tag.lower() == "center":
                (center_lat, center_lon) = cls.get_center_from_xml_dom(sub_child=sub_child)

        rel_id: Optional[int] = None
        rel_id_str: Optional[str] = child.attrib.get("id")
        if rel_id_str is not None:
            rel_id = int(rel_id_str)

        attributes = {}
        ignore = ["id"]
        for n, v in child.attrib.items():
            if n in ignore:
                continue
            attributes[n] = v

        return cls(
            rel_id=rel_id,
            attributes=attributes,
            center_lat=center_lat,
            center_lon=center_lon,
            members=members,
            tags=tags,
            result=result
        )


class RelationMember:
    """
    Base class to represent a member of a relation.
    """
    _type_value: Optional[str] = None

    def __init__(
            self,
            attributes: Optional[dict] = None,
            geometry: Optional[List["RelationWayGeometryValue"]] = None,
            ref: Optional[int] = None,
            role: Optional[str] = None,
            result: Optional[Result] = None):
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
        self.attributes = attributes
        self.geometry = geometry

    @classmethod
    def from_json(cls, data: dict, result: Optional[Result] = None) -> "RelationMember":
        """
        Create new RelationMember element from JSON data

        :param data: Element data from JSON
        :param result: The result this element belongs to
        :return: New instance of RelationMember
        :raises overpy.exception.ElementDataWrongType: If type value of the passed JSON data does not match.
        """
        if data.get("type") != cls._type_value:
            raise exception.ElementDataWrongType(
                type_expected=cls._type_value,
                type_provided=data.get("type")
            )

        ref = data.get("ref")
        role = data.get("role")

        attributes = {}
        ignore = ["geometry", "type", "ref", "role"]
        for n, v in data.items():
            if n in ignore:
                continue
            attributes[n] = v

        geometry = data.get("geometry")
        if isinstance(geometry, list):
            geometry_orig = geometry
            geometry = []
            for v in geometry_orig:
                geometry.append(
                    RelationWayGeometryValue(
                        lat=v.get("lat"),
                        lon=v.get("lon")
                    )
                )
        else:
            geometry = None

        return cls(
            attributes=attributes,
            geometry=geometry,
            ref=ref,
            role=role,
            result=result
        )

    @classmethod
    def from_xml(
            cls,
            child: xml.etree.ElementTree.Element,
            result: Optional[Result] = None) -> "RelationMember":
        """
        Create new RelationMember from XML data

        :param child: XML node to be parsed
        :param result: The result this element belongs to
        :return: New relation member oject
        :raises overpy.exception.ElementDataWrongType: If name of the xml child node doesn't match
        """
        if child.attrib.get("type") != cls._type_value:
            raise exception.ElementDataWrongType(
                type_expected=cls._type_value,
                type_provided=child.tag.lower()
            )

        ref: Optional[int] = None
        ref_str: Optional[str] = child.attrib.get("ref")
        if ref_str is not None:
            ref = int(ref_str)

        role: Optional[str] = child.attrib.get("role")

        attributes = {}
        ignore = ["geometry", "ref", "role", "type"]
        for n, v in child.attrib.items():
            if n in ignore:
                continue
            attributes[n] = v

        geometry = None
        for sub_child in child:
            if sub_child.tag.lower() == "nd":
                if geometry is None:
                    geometry = []
                geometry.append(
                    RelationWayGeometryValue(
                        lat=Decimal(sub_child.attrib["lat"]),
                        lon=Decimal(sub_child.attrib["lon"])
                    )
                )

        return cls(
            attributes=attributes,
            geometry=geometry,
            ref=ref,
            role=role,
            result=result
        )


class RelationNode(RelationMember):
    _type_value = "node"

    def resolve(self, resolve_missing: bool = False) -> Node:
        return self._result.get_node(self.ref, resolve_missing=resolve_missing)

    def __repr__(self):
        return f"<overpy.RelationNode ref={self.ref} role={self.role}>"


class RelationWay(RelationMember):
    _type_value = "way"

    def resolve(self, resolve_missing: bool = False) -> Way:
        return self._result.get_way(self.ref, resolve_missing=resolve_missing)

    def __repr__(self):
        return f"<overpy.RelationWay ref={self.ref} role={self.role}>"


class RelationWayGeometryValue:
    def __init__(self, lat: Union[Decimal, float], lon: Union[Decimal, float]):
        self.lat = lat
        self.lon = lon

    def __repr__(self):
        return f"<overpy.RelationWayGeometryValue lat={self.lat} lon={self.lon}>"


class RelationRelation(RelationMember):
    _type_value = "relation"

    def resolve(self, resolve_missing: bool = False) -> Relation:
        return self._result.get_relation(self.ref, resolve_missing=resolve_missing)

    def __repr__(self):
        return f"<overpy.RelationRelation ref={self.ref} role={self.role}>"


class RelationArea(RelationMember):
    _type_value = "area"

    def resolve(self, resolve_missing: bool = False) -> Area:
        return self._result.get_area(self.ref, resolve_missing=resolve_missing)

    def __repr__(self):
        return f"<overpy.RelationArea ref={self.ref} role={self.role}>"


class OSMSAXHandler(handler.ContentHandler):
    """
    SAX parser for Overpass XML response.
    """
    #: Tuple of opening elements to ignore
    ignore_start: ClassVar = ('osm', 'meta', 'note', 'bounds', 'remark')
    #: Tuple of closing elements to ignore
    ignore_end: ClassVar = ('osm', 'meta', 'note', 'bounds', 'remark', 'tag', 'nd', 'center')

    def __init__(self, result: Result):
        """
        :param result: Append results to this result set.
        """
        handler.ContentHandler.__init__(self)
        self._result = result
        self._curr: Dict[str, Any] = {}
        #: Current relation member object
        self.cur_relation_member: Optional[RelationMember] = None

    def startElement(self, name: str, attrs: dict):
        """
        Handle opening elements.

        :param name: Name of the element
        :param attrs: Attributes of the element
        """
        if name in self.ignore_start:
            return
        try:
            handler = getattr(self, '_handle_start_%s' % name)
        except AttributeError:
            raise KeyError("Unknown element start '%s'" % name)
        handler(attrs)

    def endElement(self, name: str):
        """
        Handle closing elements

        :param name: Name of the element
        """
        if name in self.ignore_end:
            return
        try:
            handler = getattr(self, '_handle_end_%s' % name)
        except AttributeError:
            raise KeyError("Unknown element end '%s'" % name)
        handler()

    def _handle_start_center(self, attrs: dict):
        """
        Handle opening center element

        :param attrs: Attributes of the element
        :type attrs: Dict
        """
        center_lat = attrs.get("lat")
        center_lon = attrs.get("lon")
        if center_lat is None or center_lon is None:
            raise ValueError("Unable to get lat or lon of way center.")
        self._curr["center_lat"] = Decimal(center_lat)
        self._curr["center_lon"] = Decimal(center_lon)

    def _handle_start_tag(self, attrs: dict):
        """
        Handle opening tag element

        :param attrs: Attributes of the element
        """
        try:
            tag_key = attrs['k']
        except KeyError:
            raise ValueError("Tag without name/key.")
        self._curr['tags'][tag_key] = attrs.get('v')

    def _handle_start_node(self, attrs: dict):
        """
        Handle opening node element

        :param attrs: Attributes of the element
        """
        self._curr = {
            'attributes': dict(attrs),
            'lat': None,
            'lon': None,
            'node_id': None,
            'tags': {}
        }
        if attrs.get('id', None) is not None:
            self._curr['node_id'] = int(attrs['id'])
            del self._curr['attributes']['id']
        if attrs.get('lat', None) is not None:
            self._curr['lat'] = Decimal(attrs['lat'])
            del self._curr['attributes']['lat']
        if attrs.get('lon', None) is not None:
            self._curr['lon'] = Decimal(attrs['lon'])
            del self._curr['attributes']['lon']

    def _handle_end_node(self):
        """
        Handle closing node element
        """
        self._result.append(Node(result=self._result, **self._curr))
        self._curr = {}

    def _handle_start_way(self, attrs: dict):
        """
        Handle opening way element

        :param attrs: Attributes of the element
        """
        self._curr = {
            'center_lat': None,
            'center_lon': None,
            'attributes': dict(attrs),
            'node_ids': [],
            'tags': {},
            'way_id': None
        }
        if attrs.get('id', None) is not None:
            self._curr['way_id'] = int(attrs['id'])
            del self._curr['attributes']['id']

    def _handle_end_way(self):
        """
        Handle closing way element
        """
        self._result.append(Way(result=self._result, **self._curr))
        self._curr = {}

    def _handle_start_area(self, attrs: dict):
        """
        Handle opening area element

        :param attrs: Attributes of the element
        """
        self._curr = {
            'attributes': dict(attrs),
            'tags': {},
            'area_id': None
        }
        if attrs.get('id', None) is not None:
            self._curr['area_id'] = int(attrs['id'])
            del self._curr['attributes']['id']

    def _handle_end_area(self):
        """
        Handle closing area element
        """
        self._result.append(Area(result=self._result, **self._curr))
        self._curr = {}

    def _handle_start_nd(self, attrs: dict):
        """
        Handle opening nd element

        :param attrs: Attributes of the element
        """
        if isinstance(self.cur_relation_member, RelationWay):
            if self.cur_relation_member.geometry is None:
                self.cur_relation_member.geometry = []
            self.cur_relation_member.geometry.append(
                RelationWayGeometryValue(
                    lat=Decimal(attrs["lat"]),
                    lon=Decimal(attrs["lon"])
                )
            )
        else:
            try:
                node_ref = attrs['ref']
            except KeyError:
                raise ValueError("Unable to find required ref value.")
            self._curr['node_ids'].append(int(node_ref))

    def _handle_start_relation(self, attrs: dict):
        """
        Handle opening relation element

        :param attrs: Attributes of the element
        """
        self._curr = {
            'attributes': dict(attrs),
            'members': [],
            'rel_id': None,
            'tags': {}
        }
        if attrs.get('id', None) is not None:
            self._curr['rel_id'] = int(attrs['id'])
            del self._curr['attributes']['id']

    def _handle_end_relation(self):
        """
        Handle closing relation element
        """
        self._result.append(Relation(result=self._result, **self._curr))
        self._curr = {}

    def _handle_start_member(self, attrs: dict):
        """
        Handle opening member element

        :param attrs: Attributes of the element
        """

        params: Dict[str, Any] = {
            # ToDo: Parse attributes
            'attributes': {},
            'ref': None,
            'result': self._result,
            'role': None
        }
        if attrs.get('ref', None):
            params['ref'] = int(attrs['ref'])
        if attrs.get('role', None):
            params['role'] = attrs['role']

        cls_map = {
            "area": RelationArea,
            "node": RelationNode,
            "relation": RelationRelation,
            "way": RelationWay
        }
        cls: Type[RelationMember] = cls_map.get(attrs["type"])
        if cls is None:
            raise ValueError("Undefined type for member: '%s'" % attrs['type'])

        self.cur_relation_member = cls(**params)
        self._curr['members'].append(self.cur_relation_member)

    def _handle_end_member(self):
        self.cur_relation_member = None
