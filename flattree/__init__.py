"""
FlatTree is a tool to work with nested Python dictionaries.
"""

__description__ = __doc__.strip()
__version__ = '0.1.0'
__author__ = 'Aleksandr Mikhailov'
__author_email__ = 'dev@avidclam.com'
__copyright__ = 'Copyright 2019 Aleksandr Mikhailov'

SEPARATOR = '.'

from .flatten import flatten, unflatten
from .flattreeclass import FlatTree