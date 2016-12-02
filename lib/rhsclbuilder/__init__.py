"""Top-level module
"""

import logging
import sys

__version__ = '0.1.0'

level = logging.DEBUG
LOG = logging.getLogger(__name__)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setLevel(level)
LOG.addHandler(handler)
LOG.setLevel(level)
