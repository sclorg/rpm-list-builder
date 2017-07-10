import logging

import pytest

import rpmlb.logging


@pytest.fixture
def root_logger():

    log = logging.getLogger()

    default_level = log.getEffectiveLevel()

    try:
        yield log
    finally:
        log.setLevel(default_level)


def test_configure_logging_logs_on_verbose_false(root_logger):
    rpmlb.logging.configure_logging(False)
    assert root_logger.getEffectiveLevel() == logging.INFO


def test_configure_logging_logs_on_verbose_true(root_logger):
    rpmlb.logging.configure_logging(True)
    assert root_logger.getEffectiveLevel() == logging.DEBUG
