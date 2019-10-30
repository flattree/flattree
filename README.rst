FlatTree
========

FlatTree is a lightweight tool that implements basic operations
on nested Python dictionaries, "trees".

It allows to

- merge several trees into single tree
- access leaf nodes and branches using path-like "flat" keys
- use aliases for keys
- assign or delete leaves and branches

For example, FlatTree is great when dealing with application configurations.

There might be separate setting trees for various deployment environments,
common or fallback values, with one trees shading the others.
Developer may find it concise and flexible to use `cfg['SCFMT']`
over `dev_cfg['stage']['cache']['format']` or even `cfg['stage.cache.format'] `
with full power to get back branch `{'cache': {'format': '<format value>'}}`
via simple `cfg['stage']` if needed.
