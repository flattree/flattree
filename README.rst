FlatTree
========

FlatTree is a lightweight tool that allows you to work with nested Python dictionaries, "trees":

- merge several trees into single tree
- access leaf nodes and branches using path-like linear keys
- use aliases for keys
- assign or delete leaves and branches

I often use FlatTree to access application configuration.

There may be separate trees of settings for development, sandbox, production environments, as well as trees for common or fallback values, and I need single view with simplified access to configuration variables.

For example, I'd prefer `cfg['SCFMT']` over `dev_cfg['stage']['cache']['format']` or even `cfg['stage.cache.format'] ` with full power to get back branch `{'cache': {'format': '<format value>'}}` via simple `cfg['stage']` if needed.

