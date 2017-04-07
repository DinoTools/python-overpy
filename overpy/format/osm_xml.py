from xml.sax.saxutils import escape

import overpy


def dump(result, fp):
    """
    Use the result from the Overpass API to generate OSM XML

    More information:
    
    * http://wiki.openstreetmap.org/wiki/OSM_XML

    :param result: The result from the Overpass API
    :type result: overpy.Result
    :param fp: Filepointer to use
    :return:
    """
    fp.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    fp.write('<osm version="0.6" generator="OverPy {0}">\n'.format(overpy.__version__))
    lat_min = result.nodes[0].lat
    lat_max = lat_min
    lon_min = result.nodes[0].lon
    lon_max = lon_min
    for node in result.nodes:
        if node.lat < lat_min:
            lat_min = node.lat
        elif node.lat > lat_max:
            lat_max = node.lat

        if node.lon < lon_min:
            lon_min = node.lon
        elif node.lon > lon_max:
            lon_max = node.lon

    fp.write(
        '<bounds minlat="{0:f}" minlon="{1:f}" maxlat="{2:f}" maxlon="{3:f}"/>\n'.format(
            lat_min,
            lon_min,
            lat_max,
            lon_max
        )
    )

    for node in result.nodes:
        fp.write(
            '<node id="{0:d}" lat="{1:f}" lon="{2:f}"'.format(
                node.id,
                node.lat,
                node.lon
            )
        )
        if len(node.tags) == 0:
            fp.write('/>\n')
            continue
        fp.write('>\n')
        for k, v in node.tags.items():
            fp.write(
                '<tag k="{0:s}" v="{1:s}"/>\n'.format(
                    escape(k),
                    escape(v)
                )
            )
        fp.write('</node>\n')

    for way in result.ways:
        fp.write('<way id="{0:d}"'.format(way.id))
        if len(way.nodes) == 0 and len(way.tags) == 0:
            fp.write('/>\n')
            continue
        fp.write('>\n')
        for node in way.nodes:
            fp.write('<nd ref="{0:d}"/>\n'.format(node.id))

        for k, v in way.tags.items():
            fp.write(
                '<tag k="{0:s}" v="{1:s}"/>\n'.format(
                    escape(k),
                    escape(v)
                )
            )

        fp.write('</way>\n')

    for relation in result.relations:
        fp.write('<relation id="{0:d}'.format(relation.id))
        if len(relation.tags) == 0 and len(relation.members) == 0:
            fp.write('/>\n')

        for member in relation.members:
            if not isinstance(member, overpy.RelationMember):
                continue
            fp.write(
                '<member type="{0:s}" ref="{1:d}" role="{2:s}"/>\n'.format(
                    member._type_value,
                    member.ref,
                    member.role
                )
            )

        for k, v in relation.tags.items():
            fp.write(
                '<tag k="{0:s}" v="{1:s}"/>\n'.format(
                    escape(k),
                    escape(v)
                )
            )

        fp.write('</relation>\n')

    fp.write('</osm>')
