import logging

from rhsclbuilder.builder.base import BaseBuilder
from rhsclbuilder import utils

LOG = logging.getLogger(__name__)


class CoprBuilder(BaseBuilder):
    """A builder class for Copr."""

    def build(self, package_dict, **kwargs):
        copr_repo = kwargs['copr_repo']
        if not copr_repo:
            raise ValueError('copr_repo is required.')

        utils.run_cmd('rm -v *.rpm', check=False)
        utils.run_cmd('rhpkg srpm')
        utils.run_cmd('copr-cli build %s *.rpm' % copr_repo)
