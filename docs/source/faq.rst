Frequently Asked Questions
==========================

429 Too Many Requests
---------------------

If too many requests are send from the same IP address the server blocks some requests to avoid that a user uses up all resources.
For more information have a look at the `Overpass API documentation <http://overpass-api.de/command_line.html>`_.

OverPy tries to fetch missing information automatically.
To limit the number of requests you should try to fetch all required information/data(relations, ways, nodes, tags, ...) with the initial query.
