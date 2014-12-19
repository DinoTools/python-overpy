Python Overpass Wrapper
=======================

A Python Wrapper to access the Overpass API.

Have a look at the `documentation`_ to find additional information.

.. image:: https://pypip.in/version/overpy/badge.svg
    :target: https://pypi.python.org/pypi/overpy/
    :alt: Latest Version

.. image:: https://pypip.in/license/overpy/badge.svg
    :target: https://pypi.python.org/overpy/ssdeep/
    :alt: License

.. image:: https://travis-ci.org/DinoTools/python-overpy.svg?branch=master
    :target: https://travis-ci.org/DinoTools/python-overpy

Features
--------

* Query Overpass API
* Parse JSON and XML response data

Install
-------

**Requirements:**

Supported Python versions:

* Python 2.6 and 2.7
* Python >= 3.2
* PyPy and PyPy3

**Install:**

.. code-block:: console

    $ pip install overpy

Examples
--------

Additional examples can be found in the *examples* directory.

.. code-block:: python

    import overpy

    api = overpy.Overpass()

    # fetch all ways and nodes
    result = api.query("""
        way(50.746,7.154,50.748,7.157) ["highway"];
        (._;>;);
        out body;
        """)

    for way in result.ways:
        print("Name: %s" % way.tags.get("name", "n/a"))
        print("  Highway: %s" % way.tags.get("highway", "n/a"))
        print("  Nodes:")
        for node in way.nodes:
            print("    Lat: %f, Lon: %f" % (node.lat, node.lon))


License
-------

Published under the MIT (see LICENSE for more information)

.. _`documentation`: http://python-overpy.readthedocs.org/
