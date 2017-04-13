"""Top-level module
"""

import logging

__version__ = '0.1.0'

""" Set log format considering
lavelname:
    DEBUG: 5
    INFO: 4
    WARNING: 7
    ERROR: 5
    CRITICAL: 8
name: module name
"""
LOG_FORMAT = '%(asctime)s %(levelname)-8s %(name)-26s %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
LOG = logging.getLogger(__name__)


def configure_logging(verbose):
    log_level = logging.DEBUG if verbose else logging.INFO
    LOG.setLevel(log_level)
    LOG.debug('Added logging handler to logger root at %s', __name__)
