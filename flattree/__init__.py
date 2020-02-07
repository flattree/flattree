"""
FlatTree is a tool to work with nested Python dictionaries.
"""

__title__ = __name__
__description__ = __doc__.replace('\n', ' ').replace('\r', '').strip()
__version__ = '2.0.1'
__author__ = 'Aleksandr Mikhailov'
__author_email__ = 'dev@avidclam.com'
__copyright__ = '2020 Aleksandr Mikhailov'

SEP = '.'
ESC = '\\'

from .logic import genleaves, unflatten, desparse
from .api import FlatTree