Examples
========

Basic example
-------------

Lets start with an example from the Overpass API documentation.

**Query String:**

.. code-block:: text
    :linenos:

    node(50.745,7.17,50.75,7.18);
    out;

**Use OverPy:**

.. code-block:: pycon
    :linenos:

    >>> import overpy
    >>> api = overpy.Overpass()
    >>> result = api.query("node(50.745,7.17,50.75,7.18);out;")
    >>> len(result.nodes)
    1984
    >>> len(result.ways)
    0
    >>> len(result.relations)
    0
    >>> node = result.nodes[2]
    >>> node.id
    100792806
    >>> node.tags
    {}

Line 1:
    Import the required Python module

Line 2:
    Create a new instance of the Overpass() class.
    This instance is used to query the Overpass API.

Line 3:
    Use the Query-String from above to query the Overpass API service.

Line 4,5:
    Get the number of nodes in the result set.

Line 6-9:
    Get the number of ways and relations available in the result set.

Line 10-14:
    Get the third node from the list.
    Display the ID and the tags of this node.


Use Overpass QL or Overpass XML
-------------------------------

Queries are passed directly to the Overpass API service without any modification.
So it is possible to use Overpass QL and Overpass XML.

Overpass QL
~~~~~~~~~~~

**Query:**

.. code-block:: text
    :linenos:

    node["name"="Gielgen"];
    out body;


**Use OverPy:**

.. code-block:: pycon
    :linenos:

    >>> import overpy
    >>> api = overpy.Overpass()
    >>> result = api.query("""node["name"="Gielgen"];out body;""")
    >>> len(result.nodes)
    6
    >>> len(result.ways)
    0
    >>> len(result.relations)
    0


Overpass XML
~~~~~~~~~~~~

**Query:**

.. code-block:: xml
    :linenos:

    <osm-script>
      <query type="node">
        <has-kv k="name" v="Gielgen"/>
      </query>
      <print/>
    </osm-script>

**Use OverPy:**

.. code-block:: pycon
    :linenos:

    >>> import overpy
    >>> api = overpy.Overpass()
    >>> result = api.query("""<osm-script>
    ...   <query type="node">
    ...     <has-kv k="name" v="Gielgen"/>
    ...   </query>
    ...   <print/>
    ... </osm-script>""")
    >>> len(result.nodes)
    6
    >>> len(result.ways)
    0
    >>> len(result.relations)
    0


Parse JSON or XML responses
---------------------------

On a request OverPy detects the content type from the response.

JSON response
~~~~~~~~~~~~~

**Query String:**

.. code-block:: text
    :linenos:

    [out:json];
    node(50.745,7.17,50.75,7.18);
    out;

**Use OverPy:**

.. code-block:: pycon
    :linenos:

    >>> import overpy
    >>> api = overpy.Overpass()
    >>> result = api.query("[out:json];node(50.745,7.17,50.75,7.18);out;")
    >>> len(result.nodes)
    1984
    >>> len(result.ways)
    0
    >>> len(result.relations)
    0

XML response
~~~~~~~~~~~~

**Query String:**

.. code-block:: text
    :linenos:

    [out:xml];
    node(50.745,7.17,50.75,7.18);
    out;

**Use OverPy:**

.. code-block:: pycon
    :linenos:

    >>> import overpy
    >>> api = overpy.Overpass()
    >>> result = api.query("[out:xml];node(50.745,7.17,50.75,7.18);out;")
    >>> len(result.nodes)
    1984
    >>> len(result.ways)
    0
    >>> len(result.relations)
    0

Ways
----

Get all nodes of a way
~~~~~~~~~~~~~~~~~~~~~~

In this example the Overpass API will only return the Way elements with the name "Gielgenstraße".
But there will be no Node elements in the result set.

OverPy provides a way to resolve missing nodes.

**Query String:**

.. code-block:: text
    :linenos:

    way
    ["name"="Gielgenstraße"]
    (50.7,7.1,50.8,7.25);
    out;

**Use OverPy:**

.. code-block:: pycon
    :linenos:

    >>> import overpy
    >>> api = overpy.Overpass()
    >>> result = api.query("""way["name"="Gielgenstraße"](50.7,7.1,50.8,7.25);out;""")
    >>> len(result.nodes)
    0
    >>> len(result.ways)
    4
    >>> way = result.ways[0]
    >>> way.nodes
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
        [...]
        raise exception.DataIncomplete("Resolve missing nodes is disabled")
    overpy.exception.DataIncomplete: ('Data incomplete try to improve the query to resolve the missing data', 'Resolve missing nodes is disabled')
    >>> way.get_nodes()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
        [...]
        raise exception.DataIncomplete("Resolve missing nodes is disabled")
    overpy.exception.DataIncomplete: ('Data incomplete try to improve the query to resolve the missing data', 'Resolve missing nodes is disabled')
    >>> nodes = way.get_nodes(resolve_missing=True)
    >>> len(nodes)
    13
    >>> len(result.nodes)
    13
    >>> len(way.nodes)
    13


Line 1-3:
    Send a query to the Overpass API service.

Line 4-6:
    There are 4 Way elements and 0 Node elements in the result set.

Line 7:
    Get the first way.

Line 8-19:
    Use :attr:`overpy.Way.nodes` class attribute and the :func:`overpy.Way.get_nodes()` function to get the nodes for the way.
    Both raise an exception because the nodes are not in the result set and auto resolving missing nodes is disabled.

Line 20-21:
    Use the :func:`overpy.Way.get_nodes()` function and let OverPy try to resolve the missing nodes.
    The function will return all Node elements connected with the Way element.

Line 22-25:
    The resolved nodes have been added to the result set and are available to be used again later.
