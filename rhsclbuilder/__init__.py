"""Top-level module
"""

import logging

__version__ = '0.1.0'

level = logging.DEBUG
logging.basicConfig(level=level)
LOG = logging.getLogger(__name__)
