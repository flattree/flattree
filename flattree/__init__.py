"""
FlatTree is a tool to work with nested Python dictionaries.
"""

__title__ = __name__
__description__ = __doc__.replace('\n', ' ').replace('\r', '').strip()
__version__ = '1.0.0'
__author__ = 'Aleksandr Mikhailov'
__author_email__ = 'dev@avidclam.com'
__copyright__ = '2019 Aleksandr Mikhailov'

SEP = '.'
ESC = '\\'

from .core import FlatTreeData, flatten, unflatten
from .mainclass import FlatTree
