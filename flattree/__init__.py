"""
FlatTree is a tool to work with nested Python dictionaries.
"""

__description__ = __doc__.replace('\n', ' ').replace('\r', '').strip()
__version__ = '0.1.2'
__author__ = 'Aleksandr Mikhailov'
__author_email__ = 'dev@avidclam.com'
__copyright__ = 'Copyright 2019 Aleksandr Mikhailov'

SEPARATOR = '.'

from .flatten import FlatTreeData, flatten, unflatten
from .flattreeclass import FlatTree