Data
====

Queries to get test data.

Have a look at https://overpass-turbo.eu/ to test the queries.

area-01 (2016-11-22)
--------------------

```
area[name="Troisdorf"];
out;
```

relation-03 (2016-11-23)
------------------------

```
(rel["ref"="A 555"];);
out center;
```

relation-04 (2016-11-24)
------------------------

```
(rel["ref"="A 555"];);
out geom;
```

way-03.xml (2016-11-22)
-----------------------

```
(way(225576797);>;);
out meta center;
```

way-04 (2016-11-22)
-------------------

```
(way(225576797););
out center;
```

* With empty center information to test exception, this should never happen
