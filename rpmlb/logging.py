import logging

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


def configure_logging(verbose):
    """Configure application-wide logging."""

    logging.basicConfig(format=LOG_FORMAT)

    # As logging.basicConfig() does anything only the first time it is
    # called, the root logger should be configured explicitly
    root_logger = logging.getLogger()

    log_level = logging.DEBUG if verbose else logging.INFO
    root_logger.setLevel(log_level)

    log = logging.getLogger(__name__)
    log.debug('Added logging handler to logger root at %s', __name__)
