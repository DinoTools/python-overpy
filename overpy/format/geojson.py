import json

import overpy


def dump(result, fp, nodes=False, ways=False, json_args={}):
    """

    :param result:
    :type result: overpy.Result
    :param fp:
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

    json.dump(geojson, fp, **json_args)