Introduction
============

Requirements
------------

Supported Python versions:

* Python 3.6+
* PyPy3

Installation
------------

As a Python egg
~~~~~~~~~~~~~~~

You can install the most recent version using ``pip``

.. code-block:: console

    $ pip install overpy


From a tarball release
~~~~~~~~~~~~~~~~~~~~~~

Download the most recent tarball from github, unpack it and run the following command on the command-line.

.. code-block:: console

    $ python setup.py install


Install the development version
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install git and run the following commands on the command-line.

.. code-block:: console

    $ git clone https://github.com/DinoTools/python-overpy.git
    $ cd python-overpy
    $ python setup.py install

Usage
-----

It is recommended to have a look at the documentation of the `Overpass API`_ before using OverPy.
For more examples have a look at the :doc:`examples page <example>` or in the examples directory.

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


.. _Overpass API: https://wiki.openstreetmap.org/wiki/Overpass_API
