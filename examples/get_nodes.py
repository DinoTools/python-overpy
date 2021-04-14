#!/usr/bin/env python
import overpy

api = overpy.Overpass()

# We can also see a node's metadata:
jet_deau = 60018172
result = api.query(f"node({jet_deau}); out meta;")
node = result.get_node(jet_deau)

print(
    "The node for the famous Geneva {} ({},{}) was:".format(
        node.tags['name'],
        node.lat,
        node.lon
    )
)
attrs = node.attributes

print("* last modified {}".format(attrs['timestamp']))
print("* by {} (uid: {})".format(attrs['user'], attrs['uid']))
print("* in changeset {}".format(attrs['changeset']))
