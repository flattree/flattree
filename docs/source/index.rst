FlatTree
========

FlatTree is a lightweight tool that implements basic operations
on nested Python dictionaries, "trees".
It allows to

- merge trees into single tree
- access leaf nodes or branches using path-like "flat" keys
- use aliases for keys
- assign to or delete leaves or branches

The package has no dependencies other than The Python Standard Library.

Usage example
-------------

FlatTree is quite useful when working with application configurations.
Consider an application module that stores temporary objects in a file system
cache. While in development, it's convenient to store objects in JSON format
because of its human-readable nature.
In production, objects are saved as pickles for performance.

Use FlatTree to merge configurations as needed:

.. code-block:: python

    >>> cfg_dev = {'processor': {'cache': {'format': 'json'}}}
    >>> cfg_prod = {'processor': {'cache': {'format': 'pickle'}}}
    >>> cfg_common = {'processor': {'cache': {'folder_options': ['.cache', 'cache']}},
    >>>               'logging': None}
    >>> cfg = FlatTree(cfg_dev, cfg_common)
    >>> cfg['processor.cache.format']
    'json'
    >>> cfg['processor.cache.folder.0']  # List item can be addressed individually
    '.cache'
    >>> cfg.update_aliases({'FMT': 'processor.cache.format'})
    >>> cfg['FMT']  # Access with an alias
    'json'

It's possible to update leaves and branches.
For example, consider adding logging configuration:

.. code-block:: python

    cfg['logging'] = {
        'version': 1,
        'disable_existing_loggers': False,
        'loggers': {
            '': {
                'level': 'INFO',
            },
            'my.module': {
                'level': 'DEBUG',
            },
        }
    }

Values are accessible both as "scalar" leaves and as subtrees:

.. code-block:: python

    >>> cfg.update_aliases({'loglevel': 'logging.loggers..level'})
    >>> cfg['loglevel']
    'INFO'
    >>> cfg.update_aliases({'loggers': 'logging.loggers'})
    >>> cfg['loggers']
    {'': {'level': 'INFO'}, 'my.module': {'level': 'DEBUG'}}

Installation
------------

.. code-block:: bash

    pip install flattree


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Closing remarks
---------------

Author is aware that this kind of functionality has already been implemented
a number of times elsewhere.
However, reinventing the wheel seemed a useful practice.
