import logging

from .. import utils
from ..work import Work
from .base import BaseBuilder

LOG = logging.getLogger(__name__)


class CoprBuilder(BaseBuilder):
    """A builder class for Copr."""

    def __init__(self, work: Work, copr_repo: str = None, **options):
        """Initialize the builder.

        Keyword arguments:
            work: The overview of the work to do.
            copr_repo: Name of the repository to build into.
        """

        super().__init__(work, copr_repo=copr_repo, **options)

        if copr_repo is None:
            raise ValueError('copr_repo is required.')

        #: Name of the repository to build into
        self.copr_repo = copr_repo

    def build(self, package_dict, **kwargs):

        utils.run_cmd('rm -v *.rpm', check=False)
        utils.run_cmd('rhpkg srpm')
        utils.run_cmd('copr-cli build %s *.rpm' % self.copr_repo)
