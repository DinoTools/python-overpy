import json

import overpy


def dump(result, fp, nodes=False, ways=False, json_args=None):
    """
    Use the result from the Overpass API to generate GeoJSON.
    
    More information:

    * http://geojson.org/

    :param result: The result from the Overpass API
    :type result: overpy.Result
    :param fp: Filepointer to use
    :param nodes: Export nodes
    :type nodes: bool
    :param ways: Export ways
    :type ways: bool
    :param json_args: Additional arguments passed to json.dump(...)
    :type json_args: dict
    :return:
    """
    features = []
    if nodes:
        for node in result.nodes:
            properties = {}
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        float(node.lon),
                        float(node.lat)
                    ]
                },
                "properties": properties
            })

    if ways:
        for way in result.ways:
            properties = {}
            coordinates = []
            for node in way.nodes:
                coordinates.append([
                    float(node.lon),
                    float(node.lat)
                ])
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": coordinates
                },
                "properties": properties
            })

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    if json_args is None:
        json_args = {}
    json.dump(geojson, fp, **json_args)
