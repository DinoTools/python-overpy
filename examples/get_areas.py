#!/usr/bin/env python
import overpy

api = overpy.Overpass()

# fetch all areas
# More info on http://wiki.openstreetmap.org/wiki/Overpass_API/Overpass_API_by_Example
result = api.query("""
area[name="Troisdorf"];
out;
""")

for area in result.areas:
    print(
        "Name: %s (%i)" % (
            area.tags.get("name", "n/a"),
            area.id
        )
    )
    for n, v in area.tags.items():
        print(f"  Tag: {n} = {v}")
