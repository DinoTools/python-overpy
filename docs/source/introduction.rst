Introduction
============

Requirements
------------

Supported Python versions:

* Python 2.7
* Python > 3.2
* PyPy

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

.. literalinclude:: ../../examples/get_node.py
.. literalinclude:: ../../examples/get_ways.py

