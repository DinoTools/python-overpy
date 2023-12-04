#!/usr/bin/env python
import overpy

api = overpy.Overpass()

# We can also see a node's metadata:
jet_deau = 60018172
result = api.query(f"node({jet_deau}); out meta;")
node = result.get_node(jet_deau)

print(f"The node for the famous Geneva {node.tags['name']} ({node.lat},{node.lon}) was:")
attrs = node.attributes

print(f"* last modified {attrs['timestamp']}")
print(f"* by {attrs['user']} (uid: {attrs['uid']})")
print(f"* in changeset {attrs['changeset']}")
