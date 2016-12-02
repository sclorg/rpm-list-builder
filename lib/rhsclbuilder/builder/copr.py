import logging

from rhsclbuilder.builder.base import BaseBuilder

LOG = logging.getLogger(__name__)


class CoprBuilder(BaseBuilder):
    """A builder class for Copr."""

    def build(self, **kwargs):
        # copr-cli build rh-ror50-test

