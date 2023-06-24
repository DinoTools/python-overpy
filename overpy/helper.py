from typing import List, Optional
__author__ = 'mjob'

import overpy


def get_street(
        street: str,
        areacode: str,
        api: Optional[overpy.Overpass] = None) -> overpy.Result:
    """
    Retrieve streets in a given bounding area

    :param street: Name of street
    :param areacode: The OSM id of the bounding area
    :param api: API object to fetch missing elements
    :return: Parsed result
    :raises overpy.exception.OverPyException: If something bad happens.
    """
    if api is None:
        api = overpy.Overpass()

    query = f"""
        area({areacode})->.location;
        (
            way[highway][name="{street}"](area.location);
            - (
                way[highway=service](area.location);
                way[highway=track](area.location);
            );
        );
        out body;
        >;
        out skel qt;
    """

    data = api.query(query)

    return data


def get_intersection(
        street1: str,
        street2: str,
        areacode: str,
        api: Optional[overpy.Overpass] = None) -> List[overpy.Node]:
    """
    Retrieve intersection of two streets in a given bounding area

    :param street1: Name of first street of intersection
    :param street2: Name of second street of intersection
    :param areacode: The OSM id of the bounding area
    :param api: API object to fetch missing elements
    :return: List of intersections
    :raises overpy.exception.OverPyException: If something bad happens.
    """
    if api is None:
        api = overpy.Overpass()

    query = f"""
        area({areacode}->.location;
        (
            way[highway][name="{street1}"](area.location); node(w)->.n1;
            way[highway][name="{street2}"](area.location); node(w)->.n2;
        );
        node.n1.n2;
        out meta;
    """

    data = api.query(query)

    return data.get_nodes()
